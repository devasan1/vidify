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
    id="open-sora",
    name="Open-Sora",
    category=Category.TEXT_TO_VIDEO,
    short_description="HPC-AI Open-Sora — efficient open Sora-style T2V.",
    license="Apache-2.0",
    homepage="https://github.com/hpcaitech/Open-Sora",
    inputs=[
        InputField(id="prompt", kind=InputKind.TEXT, label="Prompt"),
    ],
    params=[
        ParamField(id="resolution", kind=ParamKind.ENUM, label="Resolution", options=["240p", "360p", "480p", "720p"], default="480p"),
        ParamField(id="num_frames", kind=ParamKind.INT, label="Frames", default=102, min=17, max=204, step=17),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=24, min=8, max=30, step=1),
        ParamField(id="steps", kind=ParamKind.INT, label="Steps", default=30, min=20, max=60, step=1),
        ParamField(id="seed", kind=ParamKind.SEED, label="Seed", default=42),
    ],
    weights=[WeightSource(repo_id="hpcai-tech/Open-Sora-v2", target_subdir="open-sora", approx_size_gb=22.0)],
    vram_gb_min=16.0,
    vram_gb_recommended=24.0,
    runner="vidify.runners.open_sora:OpenSoraRunner",
    status="planned",
    tags=["t2v", "diffusion"],
)
