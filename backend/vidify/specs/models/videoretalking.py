from vidify.specs.schema import (
    Category,
    InputField,
    InputKind,
    ModelSpec,
    WeightSource,
)

SPEC = ModelSpec(
    id="videoretalking",
    name="VideoReTalking",
    category=Category.TALKING_HEAD,
    short_description="Retalking an existing video — edit an actor's speech to new audio.",
    license="Apache-2.0",
    homepage="https://github.com/OpenTalker/video-retalking",
    inputs=[
        InputField(id="video", kind=InputKind.VIDEO, label="Source video", accept=[".mp4", ".mov"]),
        InputField(id="audio", kind=InputKind.AUDIO, label="New audio", accept=[".wav", ".mp3"]),
    ],
    weights=[WeightSource(repo_id="camenduru/video-retalking", target_subdir="videoretalking", approx_size_gb=2.5)],
    vram_gb_min=8.0,
    vram_gb_recommended=12.0,
    runner="vidify.runners.videoretalking:VideoReTalkingRunner",
    status="planned",
    tags=["lipsync", "video-edit"],
)
