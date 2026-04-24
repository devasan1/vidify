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
    id="liveportrait",
    name="LivePortrait",
    category=Category.TALKING_HEAD,
    short_description="Expressive portrait animation with fine-grained control (Kwai).",
    license="Apache-2.0",
    homepage="https://github.com/KwaiVGI/LivePortrait",
    paper="https://arxiv.org/abs/2407.03168",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Portrait image", accept=[".png", ".jpg"]),
        InputField(id="video", kind=InputKind.VIDEO, label="Driving video (motion)", required=False, accept=[".mp4", ".mov"], help="Motion source. If omitted, use audio-driven mode."),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio", required=False, accept=[".wav", ".mp3"]),
    ],
    params=[
        ParamField(id="flag_relative", kind=ParamKind.BOOL, label="Relative motion", default=True, advanced=True),
        ParamField(id="flag_do_crop", kind=ParamKind.BOOL, label="Auto-crop face", default=True),
        ParamField(id="source_max_dim", kind=ParamKind.INT, label="Source max dim", default=1280, min=512, max=2048, step=64, advanced=True),
    ],
    weights=[WeightSource(repo_id="KwaiVGI/LivePortrait", target_subdir="liveportrait", approx_size_gb=3.0)],
    vram_gb_min=6.0,
    vram_gb_recommended=12.0,
    runner="vidify.runners.liveportrait:LivePortraitRunner",
    status="planned",
    tags=["portrait", "expressive", "stylized"],
)
