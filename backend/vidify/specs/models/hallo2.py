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
    id="hallo2",
    name="Hallo2",
    category=Category.TALKING_HEAD,
    short_description="Photo-real diffusion talking head — long duration, high fidelity.",
    license="MIT",
    homepage="https://github.com/fudan-generative-vision/hallo2",
    paper="https://arxiv.org/abs/2410.07718",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Portrait image", accept=[".png", ".jpg", ".jpeg"]),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio", accept=[".wav", ".mp3"]),
    ],
    params=[
        ParamField(id="pose_weight", kind=ParamKind.FLOAT, label="Pose weight", default=1.0, min=0.0, max=2.0, step=0.1, advanced=True),
        ParamField(id="face_weight", kind=ParamKind.FLOAT, label="Face weight", default=1.0, min=0.0, max=2.0, step=0.1, advanced=True),
        ParamField(id="lip_weight", kind=ParamKind.FLOAT, label="Lip weight", default=1.0, min=0.0, max=2.0, step=0.1, advanced=True),
        ParamField(id="inference_steps", kind=ParamKind.INT, label="Steps", default=40, min=20, max=100, step=1),
    ],
    weights=[WeightSource(repo_id="fudan-generative-ai/hallo2", target_subdir="hallo2", approx_size_gb=15.0)],
    vram_gb_min=16.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.hallo2:Hallo2Runner",
    status="planned",
    tags=["lipsync", "diffusion", "photoreal", "heavy"],
)
