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
    id="echomimic-v2",
    name="EchoMimicV2",
    category=Category.TALKING_HEAD,
    short_description="Alibaba's half-body audio-driven animation — expressive & full of motion.",
    license="Apache-2.0",
    homepage="https://github.com/antgroup/echomimic_v2",
    paper="https://arxiv.org/abs/2411.10061",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Reference image (half-body)", accept=[".png", ".jpg"]),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio", accept=[".wav", ".mp3"]),
    ],
    params=[
        ParamField(id="inference_steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance scale", default=2.5, min=1.0, max=7.5, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=420),
    ],
    weights=[WeightSource(repo_id="BadToBest/EchoMimicV2", target_subdir="echomimic-v2", approx_size_gb=14.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.echomimic_v2:EchoMimicV2Runner",
    status="planned",
    tags=["diffusion", "half-body", "expressive"],
)
