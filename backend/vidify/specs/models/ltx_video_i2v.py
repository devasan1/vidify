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
    id="ltx-video-i2v",
    name="LTX-Video (Image-to-Video)",
    category=Category.IMAGE_TO_VIDEO,
    short_description="Fast I2V with LTX-Video — animate a still image in seconds on 24 GB.",
    license="LTX-Video Open License",
    homepage="https://github.com/Lightricks/LTX-Video",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=121, min=25, max=257, step=8),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=24, min=8, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=60, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=3.0, min=1.0, max=7.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=0),
    ],
    weights=[WeightSource(repo_id="Lightricks/LTX-Video", target_subdir="ltx-video", approx_size_gb=20.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.ltx_video_i2v:LTXVideoI2VRunner",
    status="planned",
    tags=["i2v", "fast"],
)
