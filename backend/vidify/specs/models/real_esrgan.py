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
    id="real-esrgan",
    name="Real-ESRGAN",
    category=Category.ENHANCE,
    short_description="GAN upscaler — sharpens and enlarges video by 2x or 4x.",
    license="BSD-3-Clause",
    homepage="https://github.com/xinntao/Real-ESRGAN",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Input video"),
    ],
    params=[
        ParamField(id="scale", kind=ParamKind.ENUM, label="Upscale factor", options=["2", "4"], default="2"),
        ParamField(id="model", kind=ParamKind.ENUM, label="Model variant", options=["RealESRGAN_x4plus", "RealESRGAN_x4plus_anime_6B", "realesr-animevideov3"], default="RealESRGAN_x4plus"),
        ParamField(id="face_enhance", kind=ParamKind.BOOL, label="Face enhance (GFPGAN)", default=False),
    ],
    weights=[WeightSource(repo_id="ai-forever/Real-ESRGAN", target_subdir="real-esrgan", approx_size_gb=0.5)],
    vram_gb_min=4.0,
    vram_gb_recommended=8.0,
    runner="vidify.runners.real_esrgan:RealESRGANRunner",
    status="planned",
    tags=["enhance", "upscale"],
)
