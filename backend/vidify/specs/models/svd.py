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
    id="svd",
    name="Stable Video Diffusion",
    category=Category.IMAGE_TO_VIDEO,
    short_description="Stability AI SVD-XT — reliable 25-frame image-to-video.",
    license="Stability AI Non-Commercial",
    homepage="https://github.com/Stability-AI/generative-models",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Input image"),
    ],
    params=[
        ParamField(id="motion_bucket_id", kind=ParamKind.INT, label="Motion amount", help="Higher = more motion.", default=127, min=1, max=255, step=1),
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=25, min=14, max=25, step=1),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=7, min=6, max=24, step=1),
        ParamField(id="noise_aug", kind=ParamKind.FLOAT, label="Noise augmentation", default=0.02, min=0.0, max=0.5, step=0.01, advanced=True),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="stabilityai/stable-video-diffusion-img2vid-xt", target_subdir="svd", approx_size_gb=9.0)],
    vram_gb_min=8.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.svd:SVDRunner",
    status="planned",
    tags=["i2v"],
)
