"""Specs + categories API.

Consumed by the frontend to render the home grid, model list, and dynamic
per-model run form.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vidify.specs import get_category, get_model, list_categories, list_models
from vidify.specs.schema import CATEGORY_META

router = APIRouter(prefix="/api", tags=["specs"])


def _category_payload() -> list[dict[str, Any]]:
    payload = []
    for cat in list_categories():
        meta = CATEGORY_META.get(cat, {})
        models = list_models(cat)
        payload.append(
            {
                "id": cat.value,
                "title": meta.get("title", cat.value),
                "subtitle": meta.get("subtitle", ""),
                "icon": meta.get("icon"),
                "model_count": len(models),
            }
        )
    return payload


@router.get("/categories")
def get_categories() -> list[dict[str, Any]]:
    return _category_payload()


@router.get("/categories/{cat_id}")
def get_category_detail(cat_id: str) -> dict[str, Any]:
    cat = get_category(cat_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="unknown category")
    meta = CATEGORY_META.get(cat, {})
    models = list_models(cat)
    return {
        "id": cat.value,
        "title": meta.get("title", cat.value),
        "subtitle": meta.get("subtitle", ""),
        "models": [m.model_dump() for m in models],
    }


@router.get("/models")
def get_all_models() -> list[dict[str, Any]]:
    return [m.model_dump() for m in list_models()]


@router.get("/models/{model_id}")
def get_model_detail(model_id: str) -> dict[str, Any]:
    spec = get_model(model_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")
    return spec.model_dump()


__all__ = ["router"]
