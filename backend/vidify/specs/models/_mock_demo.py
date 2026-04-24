"""Fake model that works without a GPU — lets you exercise the full UI flow.

It animates a still image into a short video by sliding/zooming it and muxes
the uploaded audio back in. Useful for end-to-end development.
"""

from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    ParamField,
    ParamKind,
)

SPEC = ModelSpec(
    id="mock-demo",
    name="Mock Demo (CPU, no GPU required)",
    category=Category.TALKING_HEAD,
    short_description="Fake lipsync model — animates an image + audio into a video using ffmpeg only.",
    long_description=(
        "Useful for testing the UI and pipeline without loading any ML model. "
        "It does not actually lipsync; it produces a slow zoom of the image with "
        "your audio muxed in. Great for end-to-end plumbing."
    ),
    license="Apache-2.0",
    homepage="https://github.com/devasan1/vidify",
    inputs=[
        InputField(
            id="image",
            kind=InputKind.IMAGE,
            label="Face image",
            help="Any photo. A clear, frontal face works best for realistic models.",
            accept=[".png", ".jpg", ".jpeg", ".webp"],
            max_size_mb=25,
        ),
        InputField(
            id="audio",
            kind=InputKind.AUDIO,
            label="Audio clip",
            help="Speech audio to drive the animation.",
            accept=[".wav", ".mp3", ".m4a", ".flac", ".ogg"],
            max_size_mb=50,
        ),
    ],
    params=[
        ParamField(
            id="fps",
            kind=ParamKind.INT,
            label="Frames per second",
            help="Output frame rate.",
            default=25,
            min=8,
            max=60,
            step=1,
        ),
        ParamField(
            id="zoom",
            kind=ParamKind.FLOAT,
            label="Zoom amount",
            help="How much to zoom over the clip.",
            default=1.1,
            min=1.0,
            max=2.0,
            step=0.05,
            advanced=True,
        ),
    ],
    weights=[],
    vram_gb_min=0.0,
    vram_gb_recommended=0.0,
    runner="vidify.runners.mock:MockRunner",
    status="stable",
    tags=["cpu-only", "testing"],
)
