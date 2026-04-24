"""Model-weights download manager.

Thin wrapper over ``huggingface_hub.snapshot_download`` that:

* places each model's files under ``<data>/models/<target_subdir>/``
* writes a small ``.vidify-installed.json`` manifest so the UI can tell
  installed vs missing models at a glance
* supports cancellation (best-effort) and progress reporting
"""

from __future__ import annotations

import fnmatch
import json
import logging
import shutil
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from vidify.auth import get_hf_token
from vidify.config import SETTINGS
from vidify.specs.schema import ModelSpec, WeightSource

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = ".vidify-installed.json"


class DownloadStatus(str, Enum):
    NOT_INSTALLED = "not_installed"
    DOWNLOADING = "downloading"
    INSTALLED = "installed"
    FAILED = "failed"


@dataclass
class ModelInstallState:
    model_id: str
    status: DownloadStatus
    size_gb: float | None
    path: Path | None
    message: str | None = None


def _manifest_path(target_dir: Path) -> Path:
    return target_dir / MANIFEST_FILENAME


def _model_root(spec: ModelSpec) -> Path:
    sub = spec.weights[0].target_subdir if spec.weights else spec.id
    return SETTINGS.models_dir / (sub or spec.id)


def check_installed(spec: ModelSpec) -> ModelInstallState:
    if not spec.weights:
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.INSTALLED,
            size_gb=0.0,
            path=None,
            message="No weights required.",
        )

    root = _model_root(spec)
    manifest = _manifest_path(root)
    if not manifest.exists():
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.NOT_INSTALLED,
            size_gb=None,
            path=None,
        )
    try:
        meta = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.FAILED,
            size_gb=None,
            path=root,
            message="Corrupted manifest.",
        )
    return ModelInstallState(
        model_id=spec.id,
        status=DownloadStatus.INSTALLED,
        size_gb=meta.get("size_gb"),
        path=root,
    )


def _dir_size_gb(path: Path) -> float:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return round(total / (1024**3), 2)


def download_model(
    spec: ModelSpec,
    progress_cb: Callable[[float, str], None] | None = None,
    log_cb: Callable[[str], None] | None = None,
) -> ModelInstallState:
    """Download all weights for a model. Blocking.

    ``log_cb`` receives human-readable log lines (progress messages, HF
    info/warnings, and the final error on failure).
    """
    if not spec.weights:
        return check_installed(spec)

    def _log(msg: str) -> None:
        if log_cb:
            log_cb(msg)

    root = _model_root(spec)
    root.mkdir(parents=True, exist_ok=True)
    _log(f"Target: {root}")
    handler = _HFLogCapture(log_cb) if log_cb else None
    if handler:
        handler.attach()
    try:
        n = len(spec.weights)
        for idx, src in enumerate(spec.weights):
            msg = f"[{idx + 1}/{n}] Fetching {src.repo_id}"
            if src.revision:
                msg += f"@{src.revision}"
            if src.files:
                msg += f"  files={src.files}"
            _log(msg)

            # Smooth intra-source progress: compose inner byte-fraction
            # with the outer "source N of M" offset.
            def _sub_cb(inner_frac: float, inner_msg: str, _idx: int = idx) -> None:
                if progress_cb is None:
                    return
                overall = (_idx + max(0.0, min(1.0, inner_frac))) / n
                progress_cb(overall, inner_msg)

            if progress_cb:
                progress_cb(idx / n, f"Fetching {src.repo_id}…")
            _fetch_one(src, root, progress_cb=_sub_cb, log_cb=log_cb)
            _log(f"[{idx + 1}/{n}] {src.repo_id} done")
        size_gb = _dir_size_gb(root)
        _log(f"Total on disk: {size_gb} GB")
        _manifest_path(root).write_text(
            json.dumps(
                {
                    "model_id": spec.id,
                    "weights": [s.model_dump() for s in spec.weights],
                    "size_gb": size_gb,
                },
                indent=2,
            )
        )
        if progress_cb:
            progress_cb(1.0, "Done")
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.INSTALLED,
            size_gb=size_gb,
            path=root,
        )
    except Exception as e:
        logger.exception("download failed for %s", spec.id)
        _log(f"ERROR: {type(e).__name__}: {e}")
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.FAILED,
            size_gb=None,
            path=root,
            message=str(e),
        )
    finally:
        if handler:
            handler.detach()


def _fetch_one(
    src: WeightSource,
    root: Path,
    progress_cb: Callable[[float, str], None] | None = None,
    log_cb: Callable[[str], None] | None = None,
) -> None:
    from huggingface_hub import snapshot_download

    token = get_hf_token()
    total_bytes = _estimate_total_bytes(src, token)
    if log_cb and total_bytes:
        log_cb(f"Expected size: {total_bytes / (1024**3):.2f} GB")

    # Background thread polls the directory size and reports fraction.
    stop = threading.Event()
    progress_thread: threading.Thread | None = None
    if progress_cb is not None and total_bytes > 0:
        def _poll() -> None:
            while not stop.is_set():
                downloaded = _dir_size_bytes(root)
                frac = min(0.99, downloaded / total_bytes) if total_bytes else 0.0
                progress_cb(
                    frac,
                    f"{downloaded / (1024**3):.2f} / {total_bytes / (1024**3):.2f} GB",
                )
                stop.wait(0.5)

        progress_thread = threading.Thread(target=_poll, daemon=True)
        progress_thread.start()

    kwargs: dict[str, Any] = {
        "repo_id": src.repo_id,
        "local_dir": str(root),
    }
    if src.revision:
        kwargs["revision"] = src.revision
    if src.files:
        kwargs["allow_patterns"] = src.files
    if token:
        kwargs["token"] = token
    try:
        snapshot_download(**kwargs)
    finally:
        stop.set()
        if progress_thread:
            progress_thread.join(timeout=2.0)

    # Final tick so the bar settles at 100% for this source.
    if progress_cb is not None:
        progress_cb(1.0, f"{src.repo_id} complete")


def _dir_size_bytes(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                continue
    return total


def _estimate_total_bytes(src: WeightSource, token: str | None) -> int:
    """Query HF for file sizes so we can show a smooth progress bar."""
    try:
        from huggingface_hub import HfApi

        api = HfApi(token=token)
        info = api.model_info(
            src.repo_id,
            revision=src.revision,
            files_metadata=True,
        )
    except Exception:
        return 0
    total = 0
    for s in info.siblings or []:
        name = getattr(s, "rfilename", None)
        size = getattr(s, "size", None) or 0
        if not name:
            continue
        if src.files and not any(fnmatch.fnmatch(name, p) for p in src.files):
            continue
        total += size
    return total


def remove_model(spec: ModelSpec) -> None:
    root = _model_root(spec)
    if root.exists():
        shutil.rmtree(root)


class _HFLogCapture(logging.Handler):
    """Attach to huggingface_hub loggers and forward records to `log_cb`."""

    _LOGGER_NAMES = ("huggingface_hub", "filelock")

    def __init__(self, log_cb: Callable[[str], None]) -> None:
        super().__init__(level=logging.INFO)
        self._log_cb = log_cb

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._log_cb(msg)
        except Exception:
            pass

    def attach(self) -> None:
        fmt = logging.Formatter("%(levelname)s %(name)s: %(message)s")
        self.setFormatter(fmt)
        for name in self._LOGGER_NAMES:
            logging.getLogger(name).addHandler(self)

    def detach(self) -> None:
        for name in self._LOGGER_NAMES:
            logging.getLogger(name).removeHandler(self)
