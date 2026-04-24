"""Simple in-process job manager.

Runs one job at a time in a background thread. Good enough for a local desktop
app — if we later need parallel jobs across GPUs, swap for a real queue.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from vidify.config import SETTINGS
from vidify.runners.base import JobContext, load_runner
from vidify.specs.schema import ModelSpec

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    id: str
    spec_id: str
    status: JobStatus
    progress: float = 0.0
    message: str = ""
    inputs: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    output_path: str | None = None
    logs: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None

    def to_public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "spec_id": self.spec_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "output_path": self.output_path,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._queue: deque[str] = deque()
        self._lock = threading.Lock()
        self._worker: threading.Thread | None = None
        self._shutdown = threading.Event()

    def enqueue(
        self,
        spec: ModelSpec,
        inputs: dict[str, Path],
        params: dict[str, Any],
    ) -> Job:
        job = Job(
            id=uuid.uuid4().hex,
            spec_id=spec.id,
            status=JobStatus.QUEUED,
            inputs={k: str(v) for k, v in inputs.items()},
            params=params,
        )
        with self._lock:
            self._jobs[job.id] = job
            self._queue.append(job.id)
            self._ensure_worker()
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    def _ensure_worker(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._shutdown.clear()
        self._worker = threading.Thread(
            target=self._run_loop, name="vidify-jobs", daemon=True
        )
        self._worker.start()

    def _run_loop(self) -> None:
        # Import here to avoid circular import at module load time.
        from vidify.specs import get_model

        while not self._shutdown.is_set():
            with self._lock:
                job_id = self._queue.popleft() if self._queue else None
            if job_id is None:
                time.sleep(0.2)
                continue
            job = self._jobs[job_id]
            spec = get_model(job.spec_id)
            if spec is None:
                job.status = JobStatus.FAILED
                job.error = f"unknown model: {job.spec_id}"
                job.finished_at = time.time()
                continue
            self._execute(job, spec)

    def _execute(self, job: Job, spec: ModelSpec) -> None:
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        job.message = "Starting…"
        output_dir = SETTINGS.outputs_dir / job.id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.mp4"
        scratch = SETTINGS.jobs_dir / job.id
        scratch.mkdir(parents=True, exist_ok=True)

        def on_progress(frac: float, msg: str) -> None:
            job.progress = max(0.0, min(1.0, frac))
            if msg:
                job.message = msg

        ctx = JobContext(
            job_id=job.id,
            spec=spec,
            inputs={k: Path(v) for k, v in job.inputs.items()},
            params=job.params,
            output_path=output_path,
            weights_dir=SETTINGS.models_dir,
            scratch_dir=scratch,
            progress_cb=on_progress,
        )
        try:
            runner = load_runner(spec)
            produced = runner.run(ctx)
            job.output_path = str(produced)
            job.progress = 1.0
            job.status = JobStatus.SUCCEEDED
            job.message = "Done"
        except Exception as e:
            logger.exception("job %s failed", job.id)
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.message = f"Failed: {e}"
        finally:
            job.logs = ctx.logs[-200:]
            job.finished_at = time.time()

    def shutdown(self) -> None:
        self._shutdown.set()


JOBS = JobManager()
