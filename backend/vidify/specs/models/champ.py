from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    WeightSource,
)

SPEC = ModelSpec(
    id="champ",
    name="Champ",
    category=Category.CHARACTER_ANIMATION,
    short_description="Controllable human image animation with 3D parametric guidance.",
    license="MIT",
    homepage="https://github.com/fudan-generative-vision/champ",
    inputs=[
        InputField(id="reference_image", kind=InputKind.IMAGE, label="Reference image"),
        InputField(id="pose_video", kind=InputKind.VIDEO, label="Pose / SMPL guidance video"),
    ],
    weights=[WeightSource(repo_id="fudan-generative-ai/champ", target_subdir="champ", approx_size_gb=7.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.champ:ChampRunner",
    status="planned",
    tags=["character", "pose-driven", "3d-guidance"],
)
