"""Model-weights download manager.

Thin wrapper over ``huggingface_hub.snapshot_download`` that:

* places each model's files under ``<data>/models/<target_subdir>/``
* writes a small ``.vidify-installed.json`` manifest so the UI can tell
  installed vs missing models at a glance
* supports cancellation (best-effort) and progress reporting
"""

from __future__ import annotations

import json
import logging
import shutil
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
            if progress_cb:
                progress_cb(idx / n, f"Fetching {src.repo_id}…")
            _fetch_one(src, root)
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


def _fetch_one(src: WeightSource, root: Path) -> None:
    from huggingface_hub import snapshot_download

    kwargs: dict[str, Any] = {
        "repo_id": src.repo_id,
        "local_dir": str(root),
        "local_dir_use_symlinks": False,
    }
    if src.revision:
        kwargs["revision"] = src.revision
    if src.files:
        kwargs["allow_patterns"] = src.files
    token = get_hf_token()
    if token:
        kwargs["token"] = token
    snapshot_download(**kwargs)


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
