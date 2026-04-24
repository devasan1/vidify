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
    id="rife",
    name="RIFE (Frame Interpolation)",
    category=Category.ENHANCE,
    short_description="Real-time frame interpolation — smooth 60/120 fps slow-mo from any video.",
    license="MIT",
    homepage="https://github.com/megvii-research/ECCV2022-RIFE",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Input video"),
    ],
    params=[
        ParamField(id="exp", kind=ParamKind.ENUM, label="Interpolation factor", options=["2x", "4x", "8x"], default="2x"),
        ParamField(id="fps_cap", kind=ParamKind.INT, label="FPS cap", default=60, min=24, max=240, step=1, advanced=True),
    ],
    weights=[WeightSource(repo_id="imaginairy/rife", target_subdir="rife", approx_size_gb=0.2)],
    vram_gb_min=4.0,
    vram_gb_recommended=8.0,
    runner="vidify.runners.rife:RIFERunner",
    status="planned",
    tags=["enhance", "interpolation"],
)
