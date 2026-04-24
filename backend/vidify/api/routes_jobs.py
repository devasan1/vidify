"""Job submission + status endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from vidify.config import SETTINGS
from vidify.jobs import JOBS
from vidify.specs import get_model
from vidify.specs.schema import InputField, InputKind, ParamField, ParamKind

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _save_upload(upload: UploadFile, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = upload.filename or "upload"
    out = dest_dir / filename
    with out.open("wb") as f:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    return out


def _coerce_param(field: ParamField, raw: str | None) -> Any:
    if raw is None or raw == "":
        return field.default
    match field.kind:
        case ParamKind.INT | ParamKind.SEED:
            return int(raw)
        case ParamKind.FLOAT:
            return float(raw)
        case ParamKind.BOOL:
            return str(raw).lower() in ("1", "true", "yes", "on")
        case _:
            return raw


def _validate_text_input(field: InputField, raw: str | None) -> str | None:
    if raw in (None, ""):
        if field.required:
            raise HTTPException(status_code=422, detail=f"missing required input: {field.id}")
        return None
    return raw


@router.post("")
async def submit_job(
    spec_id: str = Form(...),
    params: str = Form("{}"),
    texts: str = Form("{}"),
    files: list[UploadFile] | None = None,
) -> dict[str, Any]:
    spec = get_model(spec_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown model")

    # Fail fast for specs without a real runner instead of producing a
    # cryptic "No module named ..." error deep in the worker thread.
    from vidify.runners.base import RunnerNotImplementedError, load_runner

    try:
        load_runner(spec)
    except RunnerNotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e)) from e

    files = files or []
    text_map = json.loads(texts or "{}")
    param_raw = json.loads(params or "{}")

    uploads_dir = SETTINGS.uploads_dir / spec.id
    collected: dict[str, Path | str] = {}
    file_by_name = {f.filename: f for f in files}

    for inp in spec.inputs:
        if inp.kind == InputKind.TEXT:
            val = _validate_text_input(inp, text_map.get(inp.id))
            if val is not None:
                collected[inp.id] = val
            continue

        # media input — expected to arrive as a file named `<input_id>.<ext>`
        matched = None
        for name, upload in file_by_name.items():
            if name and name.startswith(inp.id):
                matched = upload
                break
        if matched is None:
            if inp.required:
                raise HTTPException(
                    status_code=422, detail=f"missing required input: {inp.id}"
                )
            continue
        path = _save_upload(matched, uploads_dir)
        collected[inp.id] = path

    param_vals: dict[str, Any] = {}
    for p in spec.params:
        param_vals[p.id] = _coerce_param(p, param_raw.get(p.id))

    job = JOBS.enqueue(spec, {k: v for k, v in collected.items() if isinstance(v, Path)}, param_vals)
    # Keep text inputs alongside in job metadata for runners that want them:
    for k, v in collected.items():
        if isinstance(v, str):
            job.inputs[k] = v
    return job.to_public()


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="unknown job")
    return job.to_public()


@router.get("")
def list_jobs() -> list[dict[str, Any]]:
    return [j.to_public() for j in JOBS.list()]


@router.get("/{job_id}/output")
def download_output(job_id: str) -> FileResponse:
    job = JOBS.get(job_id)
    if job is None or not job.output_path:
        raise HTTPException(status_code=404, detail="no output")
    path = Path(job.output_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="output file missing")
    return FileResponse(str(path), media_type="video/mp4", filename=path.name)


@router.get("/{job_id}/logs")
def get_logs(job_id: str) -> dict[str, Any]:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="unknown job")
    return {"id": job.id, "logs": job.logs}


__all__ = ["router"]
