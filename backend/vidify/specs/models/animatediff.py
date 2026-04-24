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
    id="animatediff-controlnet",
    name="AnimateDiff + ControlNet",
    category=Category.VIDEO_TO_VIDEO,
    short_description="Video restyle with AnimateDiff motion module + ControlNet guidance.",
    license="Apache-2.0",
    homepage="https://github.com/guoyww/AnimateDiff",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Source video"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
    ],
    params=[
        ParamField(id="controlnet", kind=ParamKind.ENUM, label="ControlNet", options=["canny", "depth", "openpose", "lineart"], default="canny"),
        ParamField(id="strength", kind=ParamKind.FLOAT, label="ControlNet strength", default=0.8, min=0.0, max=1.5, step=0.05),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=60, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=7.5, min=1.0, max=15.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="guoyww/animatediff", target_subdir="animatediff", approx_size_gb=6.0)],
    vram_gb_min=10.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.animatediff:AnimateDiffRunner",
    status="planned",
    tags=["v2v", "controlnet"],
)
