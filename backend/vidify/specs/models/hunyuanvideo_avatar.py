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
    id="hunyuanvideo-avatar",
    name="HunyuanVideo-Avatar",
    category=Category.TALKING_HEAD,
    short_description="Tencent's Hunyuan talking-avatar variant — audio-driven high-fidelity portraits.",
    license="Tencent Hunyuan Community",
    homepage="https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Reference portrait"),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio"),
    ],
    params=[
        ParamField(id="inference_steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=60, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=5.0, min=1.0, max=10.0, step=0.1),
    ],
    weights=[WeightSource(repo_id="tencent/HunyuanVideo-Avatar", target_subdir="hunyuanvideo-avatar", approx_size_gb=24.0)],
    vram_gb_min=20.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.hunyuanvideo_avatar:HunyuanVideoAvatarRunner",
    status="planned",
    tags=["diffusion", "avatar", "heavy"],
)
