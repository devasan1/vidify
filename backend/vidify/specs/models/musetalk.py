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
    id="musetalk",
    name="MuseTalk",
    category=Category.TALKING_HEAD,
    short_description="Fast, high-quality audio-driven lipsync for talking faces (Tencent).",
    long_description=(
        "MuseTalk is a real-time high-quality lip-sync model. It edits the mouth "
        "region of a reference image/video to match arbitrary audio. Near real-time "
        "on a modern NVIDIA GPU and identity-preserving."
    ),
    license="MIT",
    homepage="https://github.com/TMElyralab/MuseTalk",
    paper="https://arxiv.org/abs/2410.10122",
    inputs=[
        InputField(
            id="image",
            kind=InputKind.IMAGE,
            label="Reference face image or video",
            help="Clear, near-frontal face. Higher resolution gives better results.",
            accept=[".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"],
            max_size_mb=200,
        ),
        InputField(
            id="audio",
            kind=InputKind.AUDIO,
            label="Driving audio",
            help="Speech audio. 16 kHz mono WAV is ideal; other formats auto-converted.",
            accept=[".wav", ".mp3", ".m4a", ".flac", ".ogg"],
            max_size_mb=100,
        ),
    ],
    params=[
        ParamField(
            id="fps",
            kind=ParamKind.INT,
            label="Output FPS",
            default=25,
            min=15,
            max=30,
            step=1,
        ),
        ParamField(
            id="bbox_shift",
            kind=ParamKind.INT,
            label="Mouth bbox shift (px)",
            help="Vertical shift for the detected mouth box. Tweak if lips look misaligned.",
            default=0,
            min=-20,
            max=20,
            step=1,
            advanced=True,
        ),
    ],
    weights=[
        WeightSource(
            repo_id="TMElyralab/MuseTalk",
            target_subdir="musetalk",
            approx_size_gb=2.5,
        ),
    ],
    vram_gb_min=8.0,
    vram_gb_recommended=12.0,
    runner="vidify.runners.musetalk:MuseTalkRunner",
    status="planned",
    tags=["lipsync", "realtime", "recommended"],
)
