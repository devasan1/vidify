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
    id="wan2.2-i2v",
    name="Wan 2.2 (Image-to-Video)",
    category=Category.IMAGE_TO_VIDEO,
    short_description="Animate a still image with Wan 2.2 — strong identity preservation.",
    license="Apache-2.0",
    homepage="https://github.com/Wan-Video/Wan2.2",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image", accept=[".png", ".jpg", ".jpeg", ".webp"]),
        InputField(id="prompt", kind=InputKind.TEXT, label="Motion prompt", help="Describe what should happen/move in the scene."),
        InputField(id="negative_prompt", kind=InputKind.TEXT, label="Negative prompt", required=False),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=81, min=17, max=201, step=4),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=16, min=8, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=40, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=5.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="Wan-AI/Wan2.2-I2V-A14B", target_subdir="wan2.2-i2v-a14b", approx_size_gb=28.0)],
    vram_gb_min=16.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.wan22_i2v:Wan22I2VRunner",
    status="planned",
    tags=["i2v", "diffusion"],
)
