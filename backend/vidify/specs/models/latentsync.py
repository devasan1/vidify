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
    id="latentsync",
    name="LatentSync",
    category=Category.TALKING_HEAD,
    short_description="Diffusion-based lipsync from ByteDance — top-tier accuracy.",
    license="Apache-2.0",
    homepage="https://github.com/bytedance/LatentSync",
    paper="https://arxiv.org/abs/2412.09262",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Face video", accept=[".mp4", ".mov"]),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio", accept=[".wav", ".mp3"]),
    ],
    params=[
        ParamField(id="inference_steps", kind=ParamKind.INT, label="Diffusion steps", default=20, min=10, max=50, step=1),
        ParamField(id="guidance_scale", kind=ParamKind.FLOAT, label="Guidance scale", default=1.5, min=1.0, max=3.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=1247),
    ],
    weights=[WeightSource(repo_id="ByteDance/LatentSync", target_subdir="latentsync", approx_size_gb=12.0)],
    vram_gb_min=10.0,
    vram_gb_recommended=16.0,
    runner="vidify.runners.latentsync:LatentSyncRunner",
    status="planned",
    tags=["lipsync", "diffusion", "highest-quality"],
)
