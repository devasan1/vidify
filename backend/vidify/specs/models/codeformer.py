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
    id="codeformer",
    name="CodeFormer",
    category=Category.ENHANCE,
    short_description="Robust face restoration with fidelity/quality balance.",
    license="S-Lab License 1.0",
    homepage="https://github.com/sczhou/CodeFormer",
    inputs=[InputField(id="video", kind=InputKind.VIDEO, label="Input video")],
    params=[
        ParamField(id="fidelity_weight", kind=ParamKind.FLOAT, label="Fidelity", help="0 = max quality, 1 = max fidelity to input.", default=0.5, min=0.0, max=1.0, step=0.05),
        ParamField(id="upscale", kind=ParamKind.INT, label="Upscale", default=2, min=1, max=4, step=1),
    ],
    weights=[WeightSource(repo_id="trysem/GFPGAN-CodeFormer", files=["CodeFormer.pth"], target_subdir="codeformer", approx_size_gb=0.5)],
    vram_gb_min=4.0,
    vram_gb_recommended=8.0,
    runner="vidify.runners.codeformer:CodeFormerRunner",
    status="planned",
    tags=["enhance", "face-restore"],
)
