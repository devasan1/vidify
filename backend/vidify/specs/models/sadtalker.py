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
    id="sadtalker",
    name="SadTalker",
    category=Category.TALKING_HEAD,
    short_description="Single-image talking head with full head motion & expressions.",
    license="Apache-2.0",
    homepage="https://github.com/OpenTalker/SadTalker",
    inputs=[
        InputField(id="image", kind=InputKind.IMAGE, label="Portrait image", accept=[".png", ".jpg", ".jpeg"]),
        InputField(id="audio", kind=InputKind.AUDIO, label="Driving audio", accept=[".wav", ".mp3"]),
    ],
    params=[
        ParamField(id="still", kind=ParamKind.BOOL, label="Still mode (reduce head motion)", default=False),
        ParamField(id="enhancer", kind=ParamKind.ENUM, label="Face enhancer", options=["none", "gfpgan"], default="gfpgan"),
        ParamField(id="preprocess", kind=ParamKind.ENUM, label="Preprocess", options=["crop", "resize", "full"], default="crop"),
    ],
    weights=[WeightSource(repo_id="vinthony/SadTalker", target_subdir="sadtalker", approx_size_gb=2.0)],
    vram_gb_min=6.0,
    vram_gb_recommended=8.0,
    runner="vidify.runners.sadtalker:SadTalkerRunner",
    status="planned",
    tags=["lipsync", "head-motion"],
)
