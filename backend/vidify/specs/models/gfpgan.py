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
    id="gfpgan",
    name="GFPGAN",
    category=Category.ENHANCE,
    short_description="Face restoration — fixes blurry/low-res faces in video.",
    license="Apache-2.0",
    homepage="https://github.com/TencentARC/GFPGAN",
    inputs=[InputField(id="video", kind=InputKind.VIDEO, label="Input video")],
    params=[
        ParamField(id="upscale", kind=ParamKind.INT, label="Upscale", default=2, min=1, max=4, step=1),
        ParamField(id="bg_upsampler", kind=ParamKind.ENUM, label="Background upsampler", options=["none", "realesrgan"], default="realesrgan"),
    ],
    weights=[WeightSource(repo_id="TencentARC/GFPGANv1", files=["GFPGANv1.pth"], target_subdir="gfpgan", approx_size_gb=0.3)],
    vram_gb_min=4.0,
    vram_gb_recommended=8.0,
    runner="vidify.runners.gfpgan:GFPGANRunner",
    status="planned",
    tags=["enhance", "face-restore"],
)
