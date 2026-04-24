from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    WeightSource,
)

SPEC = ModelSpec(
    id="unianimate",
    name="UniAnimate",
    category=Category.CHARACTER_ANIMATION,
    short_description="Unified human image animation with temporal attention.",
    license="Apache-2.0",
    homepage="https://github.com/ali-vilab/UniAnimate",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference image"),
        InputField(id="pose_video", kind=InputKind.VIDEO, label="Pose / motion video"),
    ],
    weights=[WeightSource(repo_id="Isi99999/UniAnimate_and_Animate-X_Models", target_subdir="unianimate", approx_size_gb=12.0)],
    vram_gb_min=10.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.unianimate:UniAnimateRunner",
    status="planned",
    tags=["character", "pose-driven"],
)
