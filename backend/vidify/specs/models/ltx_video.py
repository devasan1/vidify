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
    id="ltx-video",
    name="LTX-Video",
    category=Category.TEXT_TO_VIDEO,
    short_description="Lightricks LTX-Video — fastest open DiT, near real-time on 24 GB.",
    license="LTX-Video Open License",
    homepage="https://github.com/Lightricks/LTX-Video",
    inputs=[
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
        InputField(id="negative_prompt", kind=InputKind.TEXT, label="Negative prompt", required=False),
    ],
    params=[
        ParamField(id="width", kind=ParamKind.INT, label="Width", default=768, min=512, max=1280, step=32),
        ParamField(id="height", kind=ParamKind.INT, label="Height", default=512, min=384, max=720, step=32),
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=121, min=25, max=257, step=8),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=24, min=8, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=60, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=3.0, min=1.0, max=7.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=0),
    ],
    weights=[WeightSource(repo_id="Lightricks/LTX-Video", target_subdir="ltx-video", approx_size_gb=20.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.ltx_video:LTXVideoRunner",
    status="planned",
    tags=["t2v", "fast", "diffusion"],
)
