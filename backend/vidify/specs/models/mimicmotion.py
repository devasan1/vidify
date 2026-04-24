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
    id="mimicmotion",
    name="MimicMotion",
    category=Category.CHARACTER_ANIMATION,
    short_description="Reference image + motion video — smooth, long sequences (Tencent).",
    license="Apache-2.0",
    homepage="https://github.com/Tencent/MimicMotion",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference image"),
        InputField(id="pose_video", kind=InputKind.VIDEO, label="Pose / motion video"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=72, min=16, max=200, step=8),
        ParamField(id="tile_size", kind=ParamKind.INT, label="Tile size", default=16, min=8, max=32, step=1, advanced=True),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=25, min=15, max=50, step=1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="tencent/MimicMotion", target_subdir="mimicmotion", approx_size_gb=8.0)],
    vram_gb_min=10.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.mimicmotion:MimicMotionRunner",
    status="planned",
    tags=["character", "pose-driven"],
)
