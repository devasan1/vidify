# syntax=docker/dockerfile:1.7
#
# Vidify — local open-source AI video studio
#
# Multi-stage build:
#   1. frontend:  Node 20 compiles React/Vite into static assets
#   2. runtime :  CUDA 12.4 + Python 3.11 + ffmpeg, runs FastAPI which also
#                 serves the built frontend from /app/frontend/dist.
#
# Built image exposes port 7860 and persists all downloaded weights / user
# uploads / job outputs under /data (mount a volume at /data to keep them
# across container restarts).
#
# Build:
#     docker build -t vidify:latest .
#
# Run (GPU):
#     docker run --rm -it --gpus all \
#       -p 7860:7860 \
#       -v vidify-data:/data \
#       -e HF_TOKEN=hf_xxx \
#       vidify:latest
#
# Run (CPU-only, mock-demo only):
#     docker run --rm -it -p 7860:7860 -v vidify-data:/data vidify:latest

# ---------- stage 1: build the frontend ----------
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

# Install node deps first (cached separately from source).
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build


# ---------- stage 2: runtime ----------
# CUDA 12.4 runtime matches current PyTorch (torch 2.4+ ships cu124 wheels).
# If you're on an older driver, switch to nvidia/cuda:12.1.1-runtime-ubuntu22.04
# and install torch==2.3.* instead.
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Vidify runtime: keep all state under /data so it survives container churn.
    VIDIFY_DATA_DIR=/data \
    VIDIFY_PORT=7860 \
    VIDIFY_HOST=0.0.0.0 \
    HF_HOME=/data/.huggingface

# System deps: python, ffmpeg (required by runners), git + git-lfs (HF pulls
# some repos via git-lfs), libGL/libSM for opencv-based runners.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv python3-pip python-is-python3 \
        ffmpeg git git-lfs curl ca-certificates \
        libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend deps first so code-only edits don't bust the layer cache.
COPY backend/pyproject.toml backend/README* /app/backend/
COPY backend/vidify/__init__.py /app/backend/vidify/__init__.py
RUN pip install --upgrade pip \
    && pip install -e /app/backend

# Now copy the real backend source.
COPY backend/ /app/backend/
RUN pip install -e /app/backend

# Bring in the compiled frontend from stage 1.
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Entrypoint script: create /data skeleton, then hand off to uvicorn.
COPY <<'EOF' /app/docker-entrypoint.sh
#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$VIDIFY_DATA_DIR"/{models,uploads,outputs,jobs}
exec python -m vidify.main "$@"
EOF
RUN chmod +x /app/docker-entrypoint.sh

VOLUME ["/data"]
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${VIDIFY_PORT}/api/health" || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
