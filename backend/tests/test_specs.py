"""Sanity checks on the model spec registry and category metadata."""

from __future__ import annotations

import pytest

from vidify.specs import REGISTRY, Category, list_categories, list_models
from vidify.specs.schema import CATEGORY_META, ModelSpec


def test_registry_non_empty() -> None:
    assert len(REGISTRY) > 10


def test_every_category_has_metadata() -> None:
    for cat in list_categories():
        assert cat in CATEGORY_META
        meta = CATEGORY_META[cat]
        assert meta.get("title")
        assert meta.get("subtitle")


def test_spec_fields_sensible() -> None:
    for spec in REGISTRY.values():
        assert isinstance(spec, ModelSpec), f"{spec} not a ModelSpec"
        assert spec.id, f"{spec} missing id"
        assert spec.name, f"{spec.id} missing name"
        assert spec.runner and ":" in spec.runner, f"{spec.id} bad runner: {spec.runner}"
        assert spec.inputs, f"{spec.id} has no inputs"
        # Every input id is unique within a model.
        ids = [inp.id for inp in spec.inputs]
        assert len(ids) == len(set(ids)), f"{spec.id} has duplicate input ids"
        for p in spec.params:
            if p.min is not None and p.max is not None:
                assert p.min <= p.max, f"{spec.id}:{p.id} bad range"


@pytest.mark.parametrize("cat", list(Category))
def test_category_listing_sorted(cat: Category) -> None:
    items = list_models(cat)
    # must not crash + returns ModelSpec instances
    for m in items:
        assert m.category == cat


def test_mock_demo_present() -> None:
    assert "mock-demo" in REGISTRY
    spec = REGISTRY["mock-demo"]
    assert spec.status == "stable"
    assert spec.runner.endswith(":MockRunner")
