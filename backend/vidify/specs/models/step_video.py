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
    id="step-video-t2v",
    name="Step-Video T2V",
    category=Category.TEXT_TO_VIDEO,
    short_description="StepFun Step-Video-T2V 30B — bilingual, cinematic open T2V.",
    license="Step-Video License",
    homepage="https://github.com/stepfun-ai/Step-Video-T2V",
    inputs=[
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt (EN or ZH)"),
    ],
    params=[
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=102, min=34, max=204, step=17),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=25, min=16, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=30, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=9.0, min=1.0, max=15.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="stepfun-ai/stepvideo-t2v", target_subdir="step-video", approx_size_gb=60.0)],
    vram_gb_min=48.0,
    vram_gb_recommended=80.0,
    runner="vidify.runners.step_video:StepVideoRunner",
    status="planned",
    tags=["t2v", "diffusion", "heavy", "bilingual"],
)
