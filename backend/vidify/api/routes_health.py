"""Health and runtime info."""

from __future__ import annotations

import platform
import shutil

from fastapi import APIRouter

from vidify import __version__
from vidify.config import SETTINGS

router = APIRouter(prefix="/api", tags=["health"])


def _gpu_info() -> dict[str, str | bool]:
    info: dict[str, str | bool] = {"available": False, "backend": "none"}
    try:  # torch is optional at runtime in dev
        import torch  # type: ignore

        if torch.cuda.is_available():
            info["available"] = True
            info["backend"] = "cuda"
            info["device_name"] = torch.cuda.get_device_name(0)
            info["device_count"] = str(torch.cuda.device_count())
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            info["available"] = True
            info["backend"] = "mps"
    except Exception:  # noqa: BLE001
        pass
    return info


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "data_dir": str(SETTINGS.data_dir),
        "gpu": _gpu_info(),
    }


__all__ = ["router"]
