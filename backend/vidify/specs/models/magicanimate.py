from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    WeightSource,
)

SPEC = ModelSpec(
    id="magicanimate",
    name="MagicAnimate",
    category=Category.MOTION_TRANSFER,
    short_description="DensePose-driven motion transfer — Show Lab / ByteDance.",
    license="BSD-3-Clause",
    homepage="https://github.com/magic-research/magic-animate",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference image"),
        InputField(id="motion_video", kind=InputKind.VIDEO, label="DensePose motion video"),
    ],
    weights=[WeightSource(repo_id="zcxu-eric/MagicAnimate", target_subdir="magicanimate", approx_size_gb=6.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.magicanimate:MagicAnimateRunner",
    status="planned",
    tags=["motion-transfer"],
)
