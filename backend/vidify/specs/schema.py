"""Declarative model specifications.

Every model Vidify supports is described by a :class:`ModelSpec`. The spec is the
single source of truth consumed by:

* the frontend (to render inputs, parameters, tooltips, validation, examples)
* the downloader (to know what weights to fetch)
* the runner (to map validated user inputs into model arguments)

Adding a new model = adding one spec file + one runner class. No UI changes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    TALKING_HEAD = "talking-head"
    TEXT_TO_VIDEO = "text-to-video"
    IMAGE_TO_VIDEO = "image-to-video"
    CHARACTER_ANIMATION = "character-animation"
    MOTION_TRANSFER = "motion-transfer"
    VIDEO_TO_VIDEO = "video-to-video"
    ENHANCE = "enhance"


CATEGORY_META: dict[Category, dict[str, str]] = {
    Category.TALKING_HEAD: {
        "title": "Talking Head",
        "subtitle": "Image + audio → lipsynced video",
        "icon": "mic",
    },
    Category.TEXT_TO_VIDEO: {
        "title": "Text → Video",
        "subtitle": "Generate video from a text prompt",
        "icon": "type",
    },
    Category.IMAGE_TO_VIDEO: {
        "title": "Image → Video",
        "subtitle": "Animate a still image",
        "icon": "image",
    },
    Category.CHARACTER_ANIMATION: {
        "title": "Character Animation",
        "subtitle": "Drive a character from a pose/reference video",
        "icon": "user",
    },
    Category.MOTION_TRANSFER: {
        "title": "Motion Transfer",
        "subtitle": "Re-enact a subject with new motion",
        "icon": "activity",
    },
    Category.VIDEO_TO_VIDEO: {
        "title": "Video → Video",
        "subtitle": "Restyle or edit an existing video",
        "icon": "film",
    },
    Category.ENHANCE: {
        "title": "Enhance",
        "subtitle": "Upscale, interpolate, restore",
        "icon": "sparkles",
    },
}


class InputKind(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


class InputField(BaseModel):
    """A required or optional media/text input (dropzone or textarea on the UI)."""

    id: str
    kind: InputKind
    label: str
    required: bool = True
    help: str | None = Field(default=None, description="Plain-language usage guidance.")
    example_url: str | None = Field(
        default=None,
        description="URL of a sample input the UI can show as an example.",
    )
    accept: list[str] | None = Field(
        default=None,
        description="Accepted file extensions e.g. ['.png', '.jpg'].",
    )
    max_size_mb: int | None = None


class ParamKind(str, Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    ENUM = "enum"
    SEED = "seed"


class ParamField(BaseModel):
    """A numeric / categorical parameter exposed to the user."""

    id: str
    kind: ParamKind
    label: str
    help: str | None = None
    default: Any = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: list[str] | None = Field(default=None, description="For ENUM params.")
    advanced: bool = Field(default=False, description="Hide under 'Advanced' by default.")

    @field_validator("options")
    @classmethod
    def _check_enum_options(cls, v: list[str] | None, info: Any) -> list[str] | None:
        kind = info.data.get("kind")
        if kind == ParamKind.ENUM and not v:
            raise ValueError("enum param requires options")
        return v


class WeightSource(BaseModel):
    """A downloadable artifact for a model."""

    repo_id: str = Field(description="HuggingFace repo id, e.g. 'TMElyralab/MuseTalk'.")
    files: list[str] | None = Field(
        default=None,
        description="Specific files to download. If None, snapshot the whole repo.",
    )
    revision: str | None = None
    target_subdir: str | None = Field(
        default=None,
        description="Subdirectory under the model's cache dir to place files in.",
    )
    approx_size_gb: float | None = None


class ModelSpec(BaseModel):
    """Everything the UI and runner need to know about a single model."""

    id: str = Field(description="Stable unique id, e.g. 'musetalk'.")
    name: str = Field(description="Display name.")
    category: Category
    short_description: str
    long_description: str | None = None
    license: str = Field(description="SPDX id or short license name.")
    homepage: str | None = None
    paper: str | None = None

    inputs: list[InputField]
    params: list[ParamField] = Field(default_factory=list)
    output_kind: InputKind = InputKind.VIDEO

    weights: list[WeightSource] = Field(default_factory=list)
    vram_gb_min: float = Field(default=6.0, description="Rough minimum VRAM for this model.")
    vram_gb_recommended: float = Field(default=12.0)

    runner: str = Field(
        description="Dotted path to the runner class, e.g. 'vidify.runners.mock:MockRunner'.",
    )
    status: str = Field(
        default="planned",
        description="'stable' | 'beta' | 'experimental' | 'planned'.",
    )

    tags: list[str] = Field(default_factory=list)
