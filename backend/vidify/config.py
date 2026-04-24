"""Runtime configuration and filesystem paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _default_data_dir() -> Path:
    """Where Vidify stores model weights, uploads, outputs, and job metadata."""
    env = os.environ.get("VIDIFY_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".vidify"


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    models_dir: Path
    uploads_dir: Path
    outputs_dir: Path
    jobs_dir: Path
    host: str
    port: int
    dev_mode: bool

    @classmethod
    def load(cls) -> Settings:
        data = _default_data_dir()
        settings = cls(
            data_dir=data,
            models_dir=data / "models",
            uploads_dir=data / "uploads",
            outputs_dir=data / "outputs",
            jobs_dir=data / "jobs",
            host=os.environ.get("VIDIFY_HOST", "127.0.0.1"),
            port=int(os.environ.get("VIDIFY_PORT", "7860")),
            dev_mode=os.environ.get("VIDIFY_DEV", "0") == "1",
        )
        for p in (
            settings.data_dir,
            settings.models_dir,
            settings.uploads_dir,
            settings.outputs_dir,
            settings.jobs_dir,
        ):
            p.mkdir(parents=True, exist_ok=True)
        return settings


SETTINGS = Settings.load()
