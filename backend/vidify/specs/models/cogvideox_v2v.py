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
    id="cogvideox-v2v",
    name="CogVideoX V2V",
    category=Category.VIDEO_TO_VIDEO,
    short_description="Restyle / edit an existing video with CogVideoX.",
    license="CogVideoX-License",
    homepage="https://github.com/THUDM/CogVideo",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Source video"),
        InputField(id="prompt", kind=InputKind.TEXT, label="Edit prompt"),
    ],
    params=[
        ParamField(id="strength", kind=ParamKind.FLOAT, label="Edit strength", default=0.7, min=0.1, max=1.0, step=0.05),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=50, min=20, max=80, step=1),
        ParamField(id="cfg", kind=ParamKind.FLOAT, label="Guidance", default=6.0, min=1.0, max=10.0, step=0.1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="THUDM/CogVideoX-5b", target_subdir="cogvideox-5b", approx_size_gb=18.0)],
    vram_gb_min=12.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.cogvideox_v2v:CogVideoXV2VRunner",
    status="planned",
    tags=["v2v"],
)
