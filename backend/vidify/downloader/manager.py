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
) -> ModelInstallState:
    """Download all weights for a model. Blocking."""
    if not spec.weights:
        return check_installed(spec)

    # Lazy import so backend starts even if hf_hub missing
    from huggingface_hub import snapshot_download

    root = _model_root(spec)
    root.mkdir(parents=True, exist_ok=True)
    try:
        n = len(spec.weights)
        for idx, src in enumerate(spec.weights):
            if progress_cb:
                progress_cb(idx / n, f"Fetching {src.repo_id}…")
            _fetch_one(src, root)
        size_gb = _dir_size_gb(root)
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
        return ModelInstallState(
            model_id=spec.id,
            status=DownloadStatus.FAILED,
            size_gb=None,
            path=root,
            message=str(e),
        )


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
    snapshot_download(**kwargs)


def remove_model(spec: ModelSpec) -> None:
    root = _model_root(spec)
    if root.exists():
        shutil.rmtree(root)
