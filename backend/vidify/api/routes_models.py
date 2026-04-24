"""Model download / install management."""

from __future__ import annotations

import threading

from fastapi import APIRouter, HTTPException

from vidify.downloader import DownloadStatus, check_installed, download_model, remove_model
from vidify.specs import REGISTRY, get_model

router = APIRouter(prefix="/api/models", tags=["models"])

_download_progress: dict[str, tuple[float, str]] = {}
_download_lock = threading.Lock()


@router.get("/installed")
def list_installed() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for spec in REGISTRY.values():
        state = check_installed(spec)
        with _download_lock:
            prog = _download_progress.get(spec.id)
        out[spec.id] = {
            "status": state.status.value,
            "size_gb": state.size_gb,
            "path": str(state.path) if state.path else None,
            "message": state.message,
            "progress": prog[0] if prog else None,
            "progress_message": prog[1] if prog else None,
        }
    return out


@router.post("/{model_id}/download")
def start_download(model_id: str) -> dict[str, str]:
    spec = get_model(model_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")

    def _cb(frac: float, msg: str) -> None:
        with _download_lock:
            _download_progress[model_id] = (frac, msg)

    def _run() -> None:
        try:
            state = download_model(spec, progress_cb=_cb)
            with _download_lock:
                if state.status == DownloadStatus.INSTALLED:
                    _download_progress.pop(model_id, None)
                else:
                    _download_progress[model_id] = (0.0, state.message or "Failed")
        finally:
            pass

    t = threading.Thread(target=_run, daemon=True, name=f"dl-{model_id}")
    t.start()
    return {"status": "started"}


@router.delete("/{model_id}")
def delete_model(model_id: str) -> dict[str, str]:
    spec = get_model(model_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")
    remove_model(spec)
    return {"status": "removed"}


__all__ = ["router"]
