from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    ParamField,
    ParamKind,
    WeightSource,
)

SPEC = ModelSpec(
    id="mochi-1",
    name="Mochi-1",
    category=Category.TEXT_TO_VIDEO,
    short_description="Genmo Mochi-1 — Apache-licensed DiT with strong motion coherence.",
    license="Apache-2.0",
    homepage="https://github.com/genmoai/models",
    inputs=[
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
        InputField(id="negative_prompt", kind=InputKind.TEXT, label="Negative prompt", required=False),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=85, min=31, max=163, step=6),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=30, min=16, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=64, min=32, max=100, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=4.5, min=1.0, max=8.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="genmo/mochi-1-preview", target_subdir="mochi-1", approx_size_gb=42.0)],
    vram_gb_min=24.0,
    vram_gb_recommended=48.0,
    runner="vidify.runners.mochi:MochiRunner",
    status="planned",
    tags=["t2v", "diffusion", "heavy"],
)
