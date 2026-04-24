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
    id="wav2lip",
    name="Wav2Lip",
    category=Category.TALKING_HEAD,
    short_description="Classic, fast lipsync — low VRAM, works on almost any GPU.",
    long_description=(
        "The original speech-driven lipsync model (2020). Lower visual fidelity "
        "than newer diffusion models but extremely fast and accurate on timing. "
        "Great fallback for quick drafts."
    ),
    license="BSD-3-Clause",
    homepage="https://github.com/Rudrabha/Wav2Lip",
    paper="https://arxiv.org/abs/2008.10010",
    inputs=[
        InputField(
            id="video",
            kind=InputKind.VIDEO,
            label="Face video (or image)",
            help="Input video containing a face. Still images are auto-converted to a short clip.",
            accept=[".mp4", ".mov", ".png", ".jpg", ".jpeg"],
            max_size_mb=200,
        ),
        InputField(
            id="audio",
            kind=InputKind.AUDIO,
            label="Driving audio",
            help="Any speech audio.",
            accept=[".wav", ".mp3", ".m4a", ".flac"],
            max_size_mb=100,
        ),
    ],
    params=[
        ParamField(
            id="pads_top",
            kind=ParamKind.INT,
            label="Top pad (px)",
            default=0,
            min=0,
            max=40,
            step=1,
            advanced=True,
        ),
        ParamField(
            id="pads_bottom",
            kind=ParamKind.INT,
            label="Bottom pad (px)",
            default=10,
            min=0,
            max=40,
            step=1,
            advanced=True,
        ),
        ParamField(
            id="resize_factor",
            kind=ParamKind.INT,
            label="Downscale factor",
            help="Higher = faster, lower resolution.",
            default=1,
            min=1,
            max=4,
            step=1,
            advanced=True,
        ),
    ],
    weights=[
        WeightSource(
            repo_id="camenduru/Wav2Lip",
            target_subdir="wav2lip",
            approx_size_gb=0.5,
        ),
    ],
    vram_gb_min=4.0,
    vram_gb_recommended=6.0,
    runner="vidify.runners.wav2lip:Wav2LipRunner",
    status="planned",
    tags=["lipsync", "fast", "low-vram"],
)
