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
    id="wan-animate",
    name="Wan Animate",
    category=Category.CHARACTER_ANIMATION,
    short_description="Wan 2.x character animation variant — reference image + motion video.",
    license="Apache-2.0",
    homepage="https://github.com/Wan-Video/Wan2.2",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference character image"),
        InputField(id="pose_video", kind=InputKind.VIDEO, label="Pose / motion video"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt", required=False),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=81, min=17, max=201, step=4),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=40, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=5.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="Wan-AI/Wan2.2-Animate", target_subdir="wan-animate", approx_size_gb=28.0)],
    vram_gb_min=16.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.wan_animate:WanAnimateRunner",
    status="planned",
    tags=["character", "diffusion"],
)
