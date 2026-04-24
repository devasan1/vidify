"""Persistent app-level configuration (HuggingFace token, etc.).

Stored at ``~/.vidify/config.json`` so the user sets their token once and every
future run of the backend, CLI, and download script uses it automatically.

Lookup order for secrets like the HuggingFace token:

1. Environment variable (``HF_TOKEN`` or ``HUGGING_FACE_HUB_TOKEN``).
2. ``~/.vidify/config.json``.
3. ``huggingface_hub``'s cached login (``~/.cache/huggingface/token``).
"""

from __future__ import annotations

import contextlib
import json
import os
import stat
from pathlib import Path
from typing import Any

from vidify.config import SETTINGS

CONFIG_FILE = SETTINGS.data_dir / "config.json"


def _load() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def _save(cfg: dict[str, Any]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    # chmod 600 — the file contains an API token
    with contextlib.suppress(OSError):
        CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def get_hf_token() -> str | None:
    """Resolve the HuggingFace token, or return None if not configured."""
    for env_var in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        val = os.environ.get(env_var)
        if val:
            return val.strip()

    cfg = _load()
    val = cfg.get("hf_token")
    if val:
        return str(val).strip()

    cached = Path.home() / ".cache" / "huggingface" / "token"
    if cached.exists():
        try:
            return cached.read_text().strip() or None
        except OSError:
            pass
    return None


def set_hf_token(token: str | None) -> None:
    cfg = _load()
    if token:
        cfg["hf_token"] = token.strip()
    else:
        cfg.pop("hf_token", None)
    _save(cfg)
    # Also set in current process so already-running code picks it up.
    if token:
        os.environ["HF_TOKEN"] = token.strip()
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token.strip()
    else:
        os.environ.pop("HF_TOKEN", None)
        os.environ.pop("HUGGING_FACE_HUB_TOKEN", None)


def get_hf_token_status() -> dict[str, object]:
    """Return non-sensitive info for the UI: configured? source? masked value?"""
    sources = []
    for env_var in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        if os.environ.get(env_var):
            sources.append(f"env:{env_var}")
    if _load().get("hf_token"):
        sources.append("config-file")
    cached = Path.home() / ".cache" / "huggingface" / "token"
    if cached.exists():
        try:
            if cached.read_text().strip():
                sources.append("hf-cache")
        except OSError:
            pass

    token = get_hf_token()
    masked = _mask(token) if token else None
    return {
        "configured": bool(token),
        "sources": sources,
        "masked": masked,
    }


def _mask(token: str) -> str:
    if len(token) <= 8:
        return "•" * len(token)
    return f"{token[:4]}…{token[-4:]}"
