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
    id="animate-anyone",
    name="Animate Anyone",
    category=Category.CHARACTER_ANIMATION,
    short_description="Reference image + pose video → animated character (Alibaba).",
    license="Apache-2.0",
    homepage="https://github.com/HumanAIGC/AnimateAnyone",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference character"),
        InputField(id="pose_video", kind=InputKind.VIDEO, label="Pose / motion video"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=72, min=24, max=192, step=8),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=25, min=20, max=50, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=3.5, min=1.0, max=7.5, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="patrolli/AnimateAnyone", target_subdir="animate-anyone", approx_size_gb=6.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.animate_anyone:AnimateAnyoneRunner",
    status="planned",
    tags=["character", "pose-driven"],
)
