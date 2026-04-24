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
    id="hunyuanvideo-1.5",
    name="HunyuanVideo 1.5",
    category=Category.TEXT_TO_VIDEO,
    short_description="Tencent HunyuanVideo 1.5 — state-of-the-art open text-to-video.",
    license="Tencent Hunyuan Community",
    homepage="https://github.com/Tencent/HunyuanVideo",
    inputs=[
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
        InputField(id="negative_prompt", kind=InputKind.TEXT, label="Negative prompt", required=False),
    ],
    params=[
        ParamField(id="width", kind=ParamKind.INT, label="Width", default=1280, min=544, max=1280, step=16),
        ParamField(id="height", kind=ParamKind.INT, label="Height", default=720, min=544, max=720, step=16),
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=129, min=33, max=201, step=4),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=24, min=16, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=6.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="tencent/HunyuanVideo", target_subdir="hunyuanvideo-1.5", approx_size_gb=42.0)],
    vram_gb_min=24.0,
    vram_gb_recommended=48.0,
    runner="vidify.runners.hunyuanvideo_15:HunyuanVideo15Runner",
    status="planned",
    tags=["t2v", "diffusion", "heavy", "flagship"],
)
