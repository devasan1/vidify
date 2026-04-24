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
    id="cogvideox-5b-i2v",
    name="CogVideoX-5B I2V",
    category=Category.IMAGE_TO_VIDEO,
    short_description="CogVideoX image-to-video — 5B, good balance of VRAM and quality.",
    license="CogVideoX-License",
    homepage="https://github.com/THUDM/CogVideo",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=49, min=25, max=81, step=8),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=8, min=6, max=16, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=6.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="THUDM/CogVideoX-5b-I2V", target_subdir="cogvideox-5b-i2v", approx_size_gb=18.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.cogvideox_i2v:CogVideoXI2VRunner",
    status="planned",
    tags=["i2v"],
)
