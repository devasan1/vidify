# Vidify

A local, open-source AI video studio. Run it on your machine, open it in your browser, generate videos with any of the major open-source video/avatar models — no cloud, no subscriptions.

## What it does

Vidify is a single app that exposes every major open-source video-generation model behind one clean UI. You pick **what kind of video you want to make** (talking-head, text-to-video, image-to-video, character animation, …), pick a model, fill out a dynamic form with visual guidance for every parameter that model supports, and it runs locally on your GPU.

### Categories & models (35 specs across 7 categories)

| Category | Models |
|---|---|
| **Talking Head / Lipsync** | `mock-demo` (CPU) · MuseTalk · Wav2Lip · LatentSync · SadTalker · Hallo2 · EchoMimicV2 · LivePortrait · VideoReTalking · HunyuanVideo-Avatar |
| **Text-to-Video** | Wan 2.2 · LTX-Video · HunyuanVideo-1.5 · CogVideoX-5B · Mochi-1 · Open-Sora · Step-Video |
| **Image-to-Video** | Wan 2.2 I2V · LTX-Video I2V · CogVideoX I2V · Stable Video Diffusion · DynamiCrafter · HunyuanVideo-1.5 I2V |
| **Character Animation** | Animate Anyone · MimicMotion · Champ · UniAnimate · Wan Animate |
| **Motion Transfer** | MagicAnimate |
| **Video-to-Video** | CogVideoX V2V · AnimateDiff + ControlNet |
| **Enhance** | Real-ESRGAN · RIFE · GFPGAN · CodeFormer |

Every model has its own `ModelSpec` under [`backend/vidify/specs/models/`](backend/vidify/specs/models/). Only `mock-demo` has a CPU-only runner today; everything else is `status="planned"` — the spec, UI, weights URL, and parameter form are all wired up; the per-model inference runner lands in follow-up PRs.

## Requirements

- Linux (tested), macOS / Windows (WSL) likely fine
- Python **3.10+**
- Node.js **18+**
- **NVIDIA GPU with ≥ 8 GB VRAM** for most models (24 GB recommended for diffusion video models)
- `ffmpeg` on PATH
- ~10–200 GB free disk (depending on which models you install)

## Quick start

```bash
git clone https://github.com/devasan1/vidify.git
cd vidify
./start.sh
```

`start.sh` sets up a Python venv, installs backend + frontend deps, builds the frontend, launches FastAPI on `:7860`, and opens it in your browser.

For live hot-reload during development:

```bash
./start.sh --dev    # backend on :7860, frontend on :5173 with proxy
```

Try it without any GPU / weights — the `mock-demo` model runs pure ffmpeg and produces a real MP4 from any image + audio clip. Go to **Talking Head → Mock Demo** in the UI.

### CLI

```bash
vidify list                      # all models, marks installed ones
vidify download musetalk         # fetch one model's weights
vidify serve --dev               # run backend only

python scripts/download_models.py --category text-to-video
python scripts/download_models.py wan2.2-t2v ltx-video
```

## Architecture

```
vidify/
├── backend/            # FastAPI + PyTorch inference
│   ├── vidify/
│   │   ├── api/        # HTTP routes
│   │   ├── specs/      # ModelSpec files (one per model)
│   │   ├── runners/    # Model wrappers (MuseTalk, Wan, ...)
│   │   ├── jobs/       # In-process job queue
│   │   └── downloader/ # HuggingFace weight fetcher
│   └── tests/
├── frontend/           # React + Vite + Tailwind
│   └── src/
│       ├── pages/      # Home, Category, Model run, Model manager
│       └── components/ # Dynamic input renderer, dropzones, players
├── scripts/            # CLI tools (download_models.py, ...)
└── docs/               # Architecture, model index
```

**Design principle:** every model is described by a declarative `ModelSpec` (inputs, parameters, defaults, ranges, tooltips, VRAM, weights). The frontend reads these specs from `/api/specs` and **auto-renders the right form controls per model** — no UI code per model.

## Adding a new model

```python
# backend/vidify/specs/models/my_model.py
from vidify.specs.schema import (
    Category, InputField, InputKind, ModelSpec,
    ParamField, ParamKind, WeightSource,
)

SPEC = ModelSpec(
    id="my-model",
    name="My Model",
    category=Category.TEXT_TO_VIDEO,
    short_description="One-line pitch.",
    license="Apache-2.0",
    homepage="https://github.com/example/my-model",
    inputs=[InputField(id="prompt", kind=InputKind.TEXT, label="Prompt")],
    params=[ParamField(id="steps", kind=ParamKind.INT, default=30, min=10, max=80)],
    weights=[WeightSource(repo_id="example/my-model", approx_size_gb=12.0)],
    vram_gb_min=12.0, vram_gb_recommended=24.0,
    runner="vidify.runners.my_model:MyModelRunner",
    status="beta",
)
```

Drop the file in `backend/vidify/specs/models/` — the registry auto-discovers it, the downloader can fetch the weights, and the frontend auto-renders the form.

Then implement the runner:

```python
# backend/vidify/runners/my_model.py
from vidify.runners.base import JobContext, Runner

class MyModelRunner(Runner):
    def run(self, ctx: JobContext):
        # inference... write mp4 to ctx.output_path
        return ctx.output_path
```

## License

Apache-2.0. Individual model weights are governed by their respective upstream licenses.
