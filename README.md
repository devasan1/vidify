# Vidify

A local, open-source AI video studio. Run it on your machine, open it in your browser, generate videos with any of the major open-source video/avatar models — no cloud, no subscriptions.

## What it does

Vidify is a single app that exposes every major open-source video-generation model behind one clean UI. You pick **what kind of video you want to make** (talking-head, text-to-video, image-to-video, character animation, …), pick a model, fill out a dynamic form with visual guidance for every parameter that model supports, and it runs locally on your GPU.

### Categories & models (planned)

| Category | Models |
|---|---|
| **Talking Head / Lipsync** | MuseTalk · Wav2Lip · LatentSync · SadTalker · Hallo2 · EchoMimicV2 · LivePortrait · VideoReTalking · HunyuanVideo-Avatar |
| **Text-to-Video** | Wan 2.2 · LTX-Video · HunyuanVideo-1.5 · CogVideoX-5B · Mochi-1 · Open-Sora · Step-Video |
| **Image-to-Video** | Wan 2.2 I2V · LTX-Video I2V · CogVideoX I2V · Stable Video Diffusion · DynamiCrafter · HunyuanVideo-1.5 I2V |
| **Character Animation** | Animate Anyone · MimicMotion · Champ · UniAnimate · Wan Animate |
| **Motion Transfer** | MagicAnimate · MimicMotion |
| **Video-to-Video** | CogVideoX V2V · AnimateDiff + ControlNet |
| **Enhance** | Real-ESRGAN · RIFE / FILM · GFPGAN · CodeFormer |

See [`docs/model-index.md`](docs/model-index.md) for the full catalogue with licenses, VRAM, and status.

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

`start.sh` sets up a Python venv, installs backend + frontend deps, launches both, and opens `http://localhost:7860` in your browser.

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

## License

Apache-2.0. Individual model weights are governed by their respective upstream licenses — see [`docs/model-index.md`](docs/model-index.md).
