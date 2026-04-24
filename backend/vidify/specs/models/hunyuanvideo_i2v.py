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
    id="hunyuanvideo-1.5-i2v",
    name="HunyuanVideo 1.5 I2V",
    category=Category.IMAGE_TO_VIDEO,
    short_description="Tencent HunyuanVideo 1.5 image-to-video variant.",
    license="Tencent Hunyuan Community",
    homepage="https://github.com/Tencent/HunyuanVideo",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=129, min=33, max=201, step=4),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=24, min=16, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=6.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="tencent/HunyuanVideo-1.5", target_subdir="hunyuanvideo-1.5-i2v", approx_size_gb=42.0)],
    vram_gb_min=24.0,
    vram_gb_recommended=48.0,
    runner="vidify.runners.hunyuanvideo_i2v:HunyuanVideoI2VRunner",
    status="planned",
    tags=["i2v", "heavy"],
)
