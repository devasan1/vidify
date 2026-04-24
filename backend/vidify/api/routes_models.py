"""Model download / install management."""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, HTTPException

from vidify.downloader import DownloadStatus, check_installed, download_model, remove_model
from vidify.specs import REGISTRY, get_model

router = APIRouter(prefix="/api/models", tags=["models"])

_LOG_BUFFER_SIZE = 500


@dataclass
class DownloadState:
    status: str = "idle"  # idle | running | succeeded | failed
    progress: float = 0.0  # 0.0 .. 1.0
    message: str = ""
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None
    logs: deque[tuple[float, str]] = field(
        default_factory=lambda: deque(maxlen=_LOG_BUFFER_SIZE)
    )


class DownloadRegistry:
    """Per-model download state + logs, thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: dict[str, DownloadState] = {}

    def get(self, model_id: str) -> DownloadState | None:
        with self._lock:
            st = self._states.get(model_id)
            if st is None:
                return None
            # return a shallow copy of logs so we don't leak the deque
            return st

    def start(self, model_id: str) -> DownloadState:
        with self._lock:
            state = self._states.setdefault(model_id, DownloadState())
            state.status = "running"
            state.progress = 0.0
            state.message = "Starting…"
            state.started_at = time.time()
            state.finished_at = None
            state.error = None
            state.logs.clear()
            state.logs.append((time.time(), "Download started"))
            return state

    def log(self, model_id: str, line: str) -> None:
        with self._lock:
            state = self._states.get(model_id)
            if state is None:
                return
            state.logs.append((time.time(), line))

    def progress(self, model_id: str, fraction: float, message: str) -> None:
        with self._lock:
            state = self._states.get(model_id)
            if state is None:
                return
            state.progress = max(0.0, min(1.0, fraction))
            if message:
                state.message = message

    def finish(self, model_id: str, ok: bool, message: str) -> None:
        with self._lock:
            state = self._states.get(model_id)
            if state is None:
                return
            state.status = "succeeded" if ok else "failed"
            state.progress = 1.0 if ok else state.progress
            state.message = message
            state.finished_at = time.time()
            if not ok:
                state.error = message


_REGISTRY = DownloadRegistry()


def _serialize(model_id: str, state: DownloadState) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "status": state.status,
        "progress": state.progress,
        "message": state.message,
        "error": state.error,
        "started_at": state.started_at,
        "finished_at": state.finished_at,
        "logs": [
            {"at": ts, "line": line} for ts, line in state.logs
        ],
    }


@router.get("/installed")
def list_installed() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for spec in REGISTRY.values():
        state = check_installed(spec)
        dl = _REGISTRY.get(spec.id)
        out[spec.id] = {
            "status": state.status.value,
            "size_gb": state.size_gb,
            "path": str(state.path) if state.path else None,
            "message": state.message,
            "download": (
                {
                    "status": dl.status,
                    "progress": dl.progress,
                    "message": dl.message,
                    "error": dl.error,
                }
                if dl is not None and dl.status != "idle"
                else None
            ),
        }
    return out


@router.post("/{model_id}/download")
def start_download(model_id: str) -> dict[str, str]:
    spec = get_model(model_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")

    existing = _REGISTRY.get(model_id)
    if existing is not None and existing.status == "running":
        return {"status": "already-running"}

    _REGISTRY.start(model_id)

    def _progress_cb(frac: float, msg: str) -> None:
        _REGISTRY.progress(model_id, frac, msg)
        if msg:
            _REGISTRY.log(model_id, msg)

    def _log_cb(line: str) -> None:
        _REGISTRY.log(model_id, line)

    def _run() -> None:
        try:
            state = download_model(spec, progress_cb=_progress_cb, log_cb=_log_cb)
            if state.status == DownloadStatus.INSTALLED:
                _REGISTRY.finish(
                    model_id,
                    ok=True,
                    message=f"Installed ({state.size_gb} GB)",
                )
            else:
                _REGISTRY.finish(
                    model_id,
                    ok=False,
                    message=state.message or "Download failed",
                )
        except Exception as e:  # noqa: BLE001
            _REGISTRY.log(model_id, f"FATAL: {type(e).__name__}: {e}")
            _REGISTRY.finish(model_id, ok=False, message=str(e))

    t = threading.Thread(target=_run, daemon=True, name=f"dl-{model_id}")
    t.start()
    return {"status": "started"}


@router.get("/{model_id}/download")
def get_download_state(model_id: str) -> dict[str, Any]:
    if get_model(model_id) is None:
        raise HTTPException(status_code=404, detail="unknown model")
    state = _REGISTRY.get(model_id) or DownloadState()
    return _serialize(model_id, state)


@router.get("/{model_id}/download/logs")
def get_download_logs(model_id: str, since: float = 0.0) -> dict[str, Any]:
    """Return log lines with timestamp > since, plus the latest state.

    Clients can poll this endpoint with ``since`` set to the last timestamp
    they've seen for efficient incremental updates.
    """
    if get_model(model_id) is None:
        raise HTTPException(status_code=404, detail="unknown model")
    state = _REGISTRY.get(model_id) or DownloadState()
    lines = [
        {"at": ts, "line": line}
        for ts, line in state.logs
        if ts > since
    ]
    return {
        "model_id": model_id,
        "status": state.status,
        "progress": state.progress,
        "message": state.message,
        "error": state.error,
        "started_at": state.started_at,
        "finished_at": state.finished_at,
        "logs": lines,
        "cursor": lines[-1]["at"] if lines else since,
    }


@router.delete("/{model_id}")
def delete_model(model_id: str) -> dict[str, str]:
    spec = get_model(model_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")
    remove_model(spec)
    return {"status": "removed"}


__all__ = ["router"]
