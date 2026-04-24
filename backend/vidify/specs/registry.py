"""Loads all model specs from :mod:`vidify.specs.models`.

Each file under `models/` should define a module-level `SPEC: ModelSpec`. The
registry discovers them at import time so `REGISTRY` is a simple dict.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

from vidify.specs.schema import Category

if TYPE_CHECKING:
    from vidify.specs.schema import ModelSpec


def _discover_specs() -> dict[str, ModelSpec]:
    from vidify.specs import models as models_pkg

    specs: dict[str, ModelSpec] = {}
    for modinfo in pkgutil.iter_modules(models_pkg.__path__):
        module = importlib.import_module(f"{models_pkg.__name__}.{modinfo.name}")
        spec = getattr(module, "SPEC", None)
        if spec is None:
            continue
        if spec.id in specs:
            raise RuntimeError(f"duplicate model id: {spec.id}")
        specs[spec.id] = spec
    return specs


REGISTRY: dict[str, ModelSpec] = _discover_specs()


def list_categories() -> list[Category]:
    return list(Category)


def list_models(category: Category | None = None) -> list[ModelSpec]:
    items = list(REGISTRY.values())
    if category is not None:
        items = [m for m in items if m.category == category]
    # sort: stable > beta > experimental > planned, then by name
    order = {"stable": 0, "beta": 1, "experimental": 2, "planned": 3}
    items.sort(key=lambda m: (order.get(m.status, 9), m.name.lower()))
    return items


def get_model(model_id: str) -> ModelSpec | None:
    return REGISTRY.get(model_id)


def get_category(cat_id: str) -> Category | None:
    try:
        return Category(cat_id)
    except ValueError:
        return None
