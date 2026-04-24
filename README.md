# Vidify

A **local, open-source AI video studio**. You run it on your machine, open it in your browser, pick a category (talking-head, text-to-video, image-to-video, character animation, motion transfer, video-to-video, enhance), pick a model, fill out a dynamic form with visual guidance for every parameter that model supports, and it generates a video on your GPU. No cloud, no API keys (except a HuggingFace read token so weights can be fetched), no subscriptions.

- **34 open-source model specs** across 7 categories — all with verified HuggingFace weight URLs.
- **One UI, every model** — the frontend reads declarative `ModelSpec`s from the backend and auto-renders the right form per model.
- **Live download progress** — HuggingFace weights stream with a smooth progress bar and a log modal (real-time HF log output + per-step timestamps).
- **Extensible** — adding a new model = one spec file + one runner class. No UI code.

---

## Table of contents

- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Quick start](#quick-start)
  - [Native (recommended for dev)](#native-recommended-for-dev)
  - [Docker](#docker)
  - [CLI](#cli)
- [HuggingFace token](#huggingface-token)
- [Architecture at a glance](#architecture-at-a-glance)
- [Module-by-module tour](#module-by-module-tour)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Scripts, top-level files](#scripts-top-level-files)
- [Data on disk](#data-on-disk)
- [Adding a new model](#adding-a-new-model)
- [Development workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## What it does

Vidify exposes every major open-source video-generation model behind a single clean UI. You pick **what kind of video you want to make**, then pick a model, then fill out a form that is specific to that model. The app handles weight downloads, job queuing, progress streaming, and output playback.

### Categories & models (34 specs across 7 categories)

| Category | Models |
|---|---|
| **Talking Head / Lipsync** | `mock-demo` (CPU) · MuseTalk · Wav2Lip · LatentSync · SadTalker · Hallo2 · EchoMimicV2 · LivePortrait · VideoReTalking · HunyuanVideo-Avatar |
| **Text-to-Video** | Wan 2.2 · LTX-Video · HunyuanVideo-1.5 · CogVideoX-5B · Mochi-1 · Open-Sora v2 · Step-Video |
| **Image-to-Video** | Wan 2.2 I2V · LTX-Video I2V · CogVideoX-5B I2V · Stable Video Diffusion · DynamiCrafter · HunyuanVideo-1.5 I2V |
| **Character Animation** | Animate Anyone · MimicMotion · Champ · UniAnimate · Wan Animate |
| **Motion Transfer** | MagicAnimate |
| **Video-to-Video** | CogVideoX V2V · AnimateDiff + ControlNet |
| **Enhance** | Real-ESRGAN · RIFE · GFPGAN · CodeFormer |

Every model has its own `ModelSpec` file under [`backend/vidify/specs/models/`](backend/vidify/specs/models/). Only `mock-demo` has a CPU-only runner today; the other 33 models are `status="planned"` — the spec, UI form, weight URLs, and parameter ranges are all wired up; the per-model inference runner lands in follow-up PRs.

---

## Requirements

- **Linux** (primary target) · macOS / Windows (WSL2) likely fine for CPU-only tests
- **Python 3.10+**, **Node.js 18+**, **ffmpeg** on `PATH`
- **NVIDIA GPU** for real model inference:
  - ≥ 8 GB VRAM for Wav2Lip / SadTalker / MuseTalk / LivePortrait
  - ≥ 12 GB VRAM for LatentSync / CogVideoX / LTX-Video 2B
  - ≥ 24 GB VRAM for Wan 2.2 / LTX-Video 13B / HunyuanVideo / Hallo2 / EchoMimicV2
- ~10–200 GB free disk, depending on which models you install

Vidify runs fine **without a GPU** for exploring the UI, browsing specs, downloading weights, and running the `mock-demo` pipeline end-to-end (pure ffmpeg, no neural nets).

---

## Quick start

### Native (recommended for dev)

```bash
git clone https://github.com/devasan1/vidify.git
cd vidify
./start.sh
```

`start.sh` creates a Python venv in `backend/.venv`, installs backend + frontend deps on first run, builds the frontend, launches FastAPI on `:7860`, and opens your browser.

For live hot-reload during development:

```bash
./start.sh --dev    # backend on :7860 (uvicorn --reload), frontend on :5173 with /api proxy
```

Other flags: `--no-open`, `--port N`.

### Docker

There's a production-style multi-stage Dockerfile at the repo root.

```bash
# Optional: put your HuggingFace read token in .env first
echo 'HF_TOKEN=hf_xxx' > .env

# Build & run (GPU, via NVIDIA Container Toolkit)
docker compose up --build
```

Open <http://localhost:7860>.

What's in the image:

- **Stage 1** (`node:20-alpine`): installs `frontend/` deps, runs `npm run build` → static assets.
- **Stage 2** (`nvidia/cuda:12.4.1-runtime-ubuntu22.04`): installs `python3.11`, `ffmpeg`, `git-lfs`, OpenCV runtime libs, installs the `vidify` Python package (`pip install -e backend`), copies the built frontend from stage 1, and exposes `7860`.
- `/data` is a `VOLUME` — the container writes all model weights, uploads, and outputs there so they survive `docker compose down`. The named volume `vidify-data` in `docker-compose.yml` persists across rebuilds.
- `HEALTHCHECK` hits `/api/health` every 30s.

CPU-only: remove the `deploy.resources.reservations.devices` block from `docker-compose.yml`. `mock-demo` will still work end-to-end; neural runners will surface a clear "No CUDA" error.

### CLI

The `vidify` CLI ships with the backend package.

```bash
vidify list                     # all models, marks installed ones
vidify download musetalk        # fetch one model's weights
vidify download --category text-to-video   # a whole category
vidify auth login               # paste your HF token (persisted to config.json)
vidify auth status              # is a token configured? from where?
vidify auth logout              # forget it
vidify serve --dev              # run backend only

python scripts/download_models.py wan2.2-t2v ltx-video
python scripts/download_models.py --category enhance
```

---

## HuggingFace token

Several model repos are gated (HunyuanVideo, SVD, some Wan variants). Vidify resolves your token in this order:

1. Environment: `HF_TOKEN` · `HUGGING_FACE_HUB_TOKEN` · `HUGGINGFACE_TOKEN`
2. `<data-dir>/config.json` (written by **Settings → HuggingFace** or `vidify auth login`; `chmod 600`)
3. `huggingface_hub`'s cached login at `~/.cache/huggingface/token`

Whichever source has a value first wins. The downloader, the CLI, and the UI all use the same lookup.

---

## Architecture at a glance

```
vidify/
├── backend/                        FastAPI + PyTorch inference
│   ├── vidify/
│   │   ├── api/                    HTTP route modules
│   │   ├── auth.py                 HF token resolution + persistence
│   │   ├── cli.py                  `vidify ...` CLI (typer)
│   │   ├── config.py               filesystem paths + env-driven settings
│   │   ├── downloader/             HuggingFace weight fetcher + progress
│   │   ├── jobs/                   in-process job queue
│   │   ├── runners/                model wrappers (base class + mock + real)
│   │   ├── specs/                  ModelSpec schema + per-model spec files
│   │   └── main.py                 FastAPI app factory + uvicorn entrypoint
│   └── tests/
├── frontend/                       React + Vite + Tailwind
│   └── src/
│       ├── lib/                    API client, shared types
│       ├── components/             dynamic input renderer, download logs modal, ...
│       └── pages/                  Home, Category, Model, Jobs, Installed, Settings
├── scripts/download_models.py      CLI-only batch downloader
├── Dockerfile · docker-compose.yml · .dockerignore
├── start.sh                        one-shot launcher (native)
└── Makefile
```

**Design principle:** every model is a declarative `ModelSpec` (inputs, parameters, defaults, ranges, tooltips, VRAM, weight URLs). The frontend reads these specs from `GET /api/models` and **auto-renders** the right form controls per model — **no UI code per model**.

### End-to-end request flow

```
  browser ── POST /api/jobs (multipart: spec_id + files + params)
     │
     ▼
  routes_jobs.submit_job
     │  1. validate spec exists
     │  2. pre-load runner (raises 501 with a clear message if not implemented)
     │  3. save each upload under <data>/uploads/<spec>/
     │  4. coerce params per ParamField type
     │  5. JOBS.enqueue(...)
     ▼
  jobs.manager.Worker (background thread)
     │  - creates JobContext with validated inputs + progress_cb
     │  - runner.run(ctx) → writes mp4 to ctx.output_path
     │  - streams progress + logs to the in-memory Job
     ▼
  browser polls GET /api/jobs/{id}         (progress + logs)
  browser plays  GET /outputs/<file>.mp4   (served by FastAPI StaticFiles)
```

Parallel flow for downloads:

```
  browser ── POST /api/models/{id}/download
     │
     ▼
  routes_models.start_download  (spawns a thread)
     │
     ▼
  downloader.manager.download_model
     │  - looks up HF_TOKEN via auth.get_hf_token()
     │  - queries HfApi.model_info() to estimate total bytes
     │  - 0.5s polling thread reports downloaded/total via progress_cb
     │  - _HFLogCapture forwards huggingface_hub + filelock log records to log_cb
     │  - snapshot_download() writes to <data>/models/<subdir>/
     │  - writes .vidify-installed.json manifest on success
     ▼
  browser polls GET /api/models/{id}/download/logs?since=<cursor>
                    (state + incremental log tail — ring buffer of 500 lines)
```

---

## Module-by-module tour

### Backend

#### `vidify/config.py`

Single source of truth for filesystem layout + runtime env.

| Env var | Default | Effect |
|---|---|---|
| `VIDIFY_DATA_DIR` | `~/.vidify` | Root of all runtime state (weights/uploads/outputs/jobs/config.json) |
| `VIDIFY_HOST` | `127.0.0.1` | uvicorn bind host (Docker image sets `0.0.0.0`) |
| `VIDIFY_PORT` | `7860` | uvicorn bind port |
| `VIDIFY_DEV` | `0` | `1` enables uvicorn `--reload` and permissive CORS for Vite |

Exports a frozen `SETTINGS` dataclass and ensures every subdirectory exists on import.

#### `vidify/auth.py`

Everything HuggingFace-token-related. `get_hf_token()` walks the env → config → HF-cache lookup chain. `set_hf_token()` persists the token to `<data>/config.json` with `chmod 600` and also shoves it into the current process's env so in-flight code picks it up. `get_hf_token_status()` returns a non-sensitive snapshot (`configured`, `sources`, `masked`) for the Settings page.

#### `vidify/specs/schema.py`

Pydantic models defining what a `ModelSpec` is. Key types:

- **`Category`** — enum of the 7 top-level buckets (`talking-head`, `text-to-video`, …).
- **`InputKind`** — `TEXT`, `IMAGE`, `AUDIO`, `VIDEO`, `FILE`. Drives which dropzone/input the frontend shows.
- **`ParamKind`** — `INT`, `FLOAT`, `BOOL`, `ENUM`, `SEED`. Drives slider vs toggle vs dropdown.
- **`InputField`** — `id`, `kind`, `label`, `help`, `required`, file-type hints (e.g. accepted extensions).
- **`ParamField`** — `id`, `kind`, `label`, `help`, `default`, `min`, `max`, `step`, `options` (for ENUM).
- **`WeightSource`** — `repo_id` (HuggingFace), optional `revision`, optional `files` allow-patterns, `target_subdir`, `approx_size_gb`.
- **`ModelSpec`** — aggregates all of the above plus descriptive metadata (name, license, homepage, paper, tags, VRAM recommendations, runner dotted path, `status`).

The `status` field (`stable` / `beta` / `planned`) is how the UI knows whether to enable the Generate button.

#### `vidify/specs/models/*.py`

One file per model. Each file imports the schema and exports a `SPEC = ModelSpec(...)`. 34 of these today. Touching one file is the only change needed to add, remove, or retune a model's parameters.

Example shape:

```python
SPEC = ModelSpec(
    id="musetalk",
    name="MuseTalk",
    category=Category.TALKING_HEAD,
    short_description="Near-real-time lipsync for image+audio.",
    license="MIT",
    homepage="https://github.com/TMElyralab/MuseTalk",
    inputs=[
        InputField(id="face", kind=InputKind.IMAGE, label="Face image", required=True, help="Clear frontal face, ≥512 px."),
        InputField(id="audio", kind=InputKind.AUDIO, label="Audio", required=True, help="WAV/MP3, 16 kHz preferred."),
    ],
    params=[
        ParamField(id="bbox_shift", kind=ParamKind.INT, label="Bbox shift", default=0, min=-50, max=50),
        ParamField(id="fps", kind=ParamKind.INT, label="FPS", default=25, min=15, max=30),
    ],
    weights=[WeightSource(repo_id="TMElyralab/MuseTalk", target_subdir="musetalk", approx_size_gb=8.0)],
    vram_gb_min=8.0, vram_gb_recommended=12.0,
    runner="vidify.runners.musetalk:MuseTalkRunner",
    status="planned",
)
```

#### `vidify/specs/registry.py`

Auto-discovers every `SPEC` in `specs/models/`. Exposes `list_models()`, `get_model(id)`, and category-filtering helpers. No registration decorators — drop a file in the folder and it appears in the UI.

#### `vidify/downloader/manager.py`

HuggingFace weights fetcher. Responsibilities:

- `check_installed(spec)` — returns `ModelInstallState` by reading `<data>/models/<subdir>/.vidify-installed.json`.
- `download_model(spec, progress_cb, log_cb)` — downloads every `WeightSource`:
  - Estimates total bytes via `HfApi.model_info(files_metadata=True)` and `allow_patterns`.
  - Starts a 0.5s polling thread that reports `downloaded_bytes / total_bytes` + a `"X.XX / Y.YY GB"` message to `progress_cb`.
  - Attaches `_HFLogCapture` to the `huggingface_hub` + `filelock` loggers so their records (plus the manager's own progress lines) flow into `log_cb`.
  - Calls `snapshot_download(repo_id, local_dir, revision, allow_patterns, token)`.
  - On success, writes the install manifest (`model_id`, `weights`, `size_gb`).
  - On failure, returns a `FAILED` state with the exception message so the UI can surface it.

#### `vidify/runners/base.py`

- `JobContext` — the validated-inputs-plus-paths struct handed to a runner.
- `Runner` — ABC with a single `run(ctx) -> Path` method.
- `RunnerNotImplementedError` — raised by `load_runner(spec)` when the runner module or class is missing. Callers translate this into a `501 Not Implemented` with a clear message instead of letting the worker thread crash on a cryptic `ModuleNotFoundError`.

#### `vidify/runners/mock.py`

The only runner that's implemented today. Takes any image + audio and uses ffmpeg to produce a real MP4 (still image + audio stream, duration = audio length). Proves the whole pipeline — validation → queue → worker → progress → output streaming → `<video>` tag — on any machine, GPU or not.

#### `vidify/jobs/manager.py`

Single-worker, single-process job queue. `JOBS.enqueue(spec, inputs, params)` returns a `Job` whose state the API polls. The worker loop:

1. Pops a job.
2. Builds `JobContext` (paths under `<data>/jobs/<id>/`).
3. `runner.run(ctx)`.
4. Writes `job.output_path` + sets status to `succeeded` / `failed`.
5. Persists a JSON snapshot so jobs survive a restart.

No external broker, no Redis — keep it simple until real runners land.

#### `vidify/api/*.py`

Routes are small and focused:

- `routes_health.py` — `GET /api/health` returns version, python, platform, ffmpeg availability, GPU detection.
- `routes_specs.py` — `GET /api/models`, `GET /api/models/{id}`, `GET /api/categories`. Dumps spec data to the frontend.
- `routes_models.py` — downloads + installed state:
  - `GET /api/models/installed` — map of `id → InstallState` (with embedded current download state: status, progress, error).
  - `POST /api/models/{id}/download` — starts a background download thread; returns `{status: "started" | "already-running"}`.
  - `GET /api/models/{id}/download` — snapshot of the download state.
  - `GET /api/models/{id}/download/logs?since=<ts>` — incremental log tail (cursor-based pagination against a 500-line ring buffer per model).
  - `DELETE /api/models/{id}` — delete downloaded weights.
- `routes_jobs.py` — `POST /api/jobs` (multipart: spec_id + files + params + texts), `GET /api/jobs`, `GET /api/jobs/{id}`. Pre-loads the runner so planned models fail fast with a useful error.
- `routes_settings.py` — `GET/PUT/DELETE /api/settings/hf-token` for the Settings page.

Route ordering matters: `models_router` is registered **before** `specs_router` so the literal path `/api/models/installed` matches its handler instead of being shadowed by `/api/models/{model_id}`.

#### `vidify/main.py`

FastAPI app factory. Wires the routers, mounts the built frontend (`frontend/dist`) at `/` with SPA fallback, mounts `/outputs/` for generated videos, and runs uvicorn.

#### `vidify/cli.py`

`typer`-based CLI: `list`, `download`, `serve`, `auth login/status/logout`. Thin wrapper around the same backend modules — no duplicated logic.

### Frontend

`frontend/src/`:

- `lib/api.ts` — typed client for every backend route. Central place for `/api/...` calls.
- `lib/types.ts` — TypeScript mirrors of the backend Pydantic schemas.
- `pages/Home.tsx` — category grid.
- `pages/Category.tsx` — list of models in a category with status chips.
- `pages/Model.tsx` — the heart of the UX:
  - Header with VRAM, license, weight size, homepage/paper links.
  - "Weights not installed" card with Download button + View logs button (only when a download is active).
  - "Runner not implemented yet" banner for `status === "planned"` specs.
  - `<InputRenderer>` — dynamic form generated from `model.inputs` + `model.params`.
  - Sticky footer with validation messages + Generate button.
- `pages/Installed.tsx` — per-row Download/Remove/Logs buttons, inline progress bars, installed-total header.
- `pages/Jobs.tsx` / `pages/Job.tsx` — job history + single-job detail with live progress and `<video>` preview.
- `pages/Settings.tsx` — HF token paste/update/clear with "source" + masked display.
- `components/InputRenderer.tsx` — reads `InputField` + `ParamField` arrays and renders the right control for each: text box, textarea, image dropzone with preview thumb, audio dropzone with waveform, video dropzone with `<video>` preview, int/float sliders, bool toggles, enum dropdowns, seed input with 🎲 randomize.
- `components/DownloadLogsModal.tsx` — polls `/api/models/{id}/download/logs?since=<cursor>` every second, merges new lines into a ring, auto-scrolls, shows a status chip + progress bar + inline error callout.
- `components/Dropzone.tsx`, `VideoPlayer.tsx`, `Waveform.tsx`, etc. — small reusable pieces.

### Scripts, top-level files

- `start.sh` — one-shot launcher: venv + deps + build + serve. Supports `--dev`, `--no-open`, `--port`.
- `scripts/download_models.py` — CLI-only batch downloader (same backend as the UI).
- `Makefile` — `make install`, `make dev`, `make test`, `make lint`, `make build`.
- `Dockerfile` + `docker-compose.yml` + `.dockerignore` — see [Docker](#docker) above.

---

## Data on disk

Everything runtime lives under `VIDIFY_DATA_DIR` (default `~/.vidify`, Docker default `/data`):

```
<data-dir>/
├── config.json                       HF token + misc settings (chmod 600)
├── models/
│   └── <target_subdir>/              one per model spec
│       ├── <weights…>
│       └── .vidify-installed.json    {model_id, weights, size_gb}
├── uploads/<spec_id>/<files>         user-submitted files, kept per-spec
├── outputs/<job_id>.mp4              generated videos (served at /outputs/)
└── jobs/<job_id>.json                job metadata snapshots
```

Nothing outside this directory is written. Delete it and you're back to a clean install.

---

## Adding a new model

1. Drop a new spec file in `backend/vidify/specs/models/my_model.py`:

   ```python
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

   The registry auto-discovers it, the downloader can already fetch the weights, and the frontend auto-renders the form.

2. Implement the runner in `backend/vidify/runners/my_model.py`:

   ```python
   from vidify.runners.base import JobContext, Runner

   class MyModelRunner(Runner):
       def run(self, ctx: JobContext):
           # load weights from ctx.weights_dir, run inference, write mp4
           return ctx.output_path
   ```

3. Flip `status` to `"stable"` once it works end-to-end.

---

## Development workflow

```bash
./start.sh --dev             # backend :7860 hot-reload, frontend :5173 with /api proxy

# Inside backend/
ruff check .
python -m pytest -q

# Inside frontend/
npm run build
npm run lint
```

Tests live under `backend/tests/`. CI-friendly (`make test`).

Commit style: small, frequent, scoped. Every commit in this branch documents exactly what landed and why.

---

## Troubleshooting

- **"No module named 'vidify.runners.<foo>'"** when generating — expected for any spec with `status="planned"`. Only `mock-demo` currently has a runner. The Generate button is disabled and the UI shows a blue "Runner not implemented yet" banner for those specs.
- **HF 401 / gated repo** during download — set `HF_TOKEN` in env, or log in via **Settings → HuggingFace** (UI), or `vidify auth login` (CLI).
- **`ffmpeg: command not found`** — install it (`apt install ffmpeg` / `brew install ffmpeg`). `mock-demo` requires it; most real runners do too.
- **Slow 0 → 100 % jump on a tiny download** — the polling thread samples at 2 Hz and small files (< 200 MB on a fast connection) can finish within one tick. Expected.
- **Docker: CUDA not available** inside the container — install the NVIDIA Container Toolkit, then `docker run --gpus all ...` (or use `docker compose up` which already requests `devices: [gpu]`).

---

## License

Apache-2.0. See [`LICENSE`](LICENSE). Individual models keep their own upstream licenses — the spec files record each one.
