"""App-level settings (HuggingFace token, etc.)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vidify.auth import get_hf_token_status, set_hf_token

router = APIRouter(prefix="/api/settings", tags=["settings"])


class HFTokenBody(BaseModel):
    token: str


@router.get("/hf-token")
def hf_token_status() -> dict[str, object]:
    return get_hf_token_status()


@router.put("/hf-token")
def set_token(body: HFTokenBody) -> dict[str, object]:
    token = body.token.strip()
    if not token:
        raise HTTPException(status_code=422, detail="empty token")
    set_hf_token(token)
    return get_hf_token_status()


@router.delete("/hf-token")
def clear_token() -> dict[str, object]:
    set_hf_token(None)
    return get_hf_token_status()


__all__ = ["router"]
