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
    id="wan2.2-t2v",
    name="Wan 2.2 (Text-to-Video)",
    category=Category.TEXT_TO_VIDEO,
    short_description="Alibaba Wan 2.2 — flagship open text-to-video with strong prompt adherence.",
    long_description=(
        "Wan 2.2 is Alibaba's open-source video DiT. Produces cinematic results at "
        "720p/1080p. 14B-parameter MoE variant recommended; 5B dense variant runs on less VRAM."
    ),
    license="Apache-2.0",
    homepage="https://github.com/Wan-Video/Wan2.2",
    inputs=[
        InputField(
            id="prompt",
            kind=InputKind.TEXT,
            label="Prompt",
            help="Describe the scene, subject, motion, and style. Be specific about camera and lighting.",
        ),
        InputField(
            id="negative_prompt",
            kind=InputKind.TEXT,
            label="Negative prompt",
            required=False,
            help="What to avoid (e.g. 'blurry, low quality, extra limbs').",
        ),
    ],
    params=[
        ParamField(id="variant", kind=ParamKind.ENUM, label="Variant", options=["T2V-A14B", "T2V-5B"], default="T2V-A14B", help="14B MoE = best quality, 5B = lower VRAM."),
        ParamField(id="width", kind=ParamKind.INT, label="Width", default=1280, min=480, max=1920, step=8),
        ParamField(id="height", kind=ParamKind.INT, label="Height", default=720, min=480, max=1088, step=8),
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=81, min=17, max=201, step=4, help="Frame count. Wan uses 4n+1."),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=16, min=8, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Denoising steps", default=40, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=5.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[
        WeightSource(repo_id="Wan-AI/Wan2.2-T2V-A14B", target_subdir="wan2.2-t2v-a14b", approx_size_gb=28.0),
    ],
    vram_gb_min=16.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.wan22_t2v:Wan22T2VRunner",
    status="planned",
    tags=["t2v", "diffusion", "flagship"],
)
