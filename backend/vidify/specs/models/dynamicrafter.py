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
    id="dynamicrafter",
    name="DynamiCrafter",
    category=Category.IMAGE_TO_VIDEO,
    short_description="Image-to-video with rich prompt control — CUHK / Tencent.",
    license="Apache-2.0",
    homepage="https://github.com/Doubiiu/DynamiCrafter",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Motion prompt"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=16, min=8, max=32, step=1),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=8, min=4, max=16, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=25, max=100, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=7.5, min=1.0, max=15.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="Doubiiu/DynamiCrafter_1024", target_subdir="dynamicrafter", approx_size_gb=10.0)],
    vram_gb_min=10.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.dynamicrafter:DynamiCrafterRunner",
    status="planned",
    tags=["i2v"],
)
