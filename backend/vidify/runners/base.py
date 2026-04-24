"""Base classes for model runners.

A :class:`Runner` implements a single model's inference. It is instantiated by
the job manager per job, receives a :class:`JobContext` with validated inputs
and progress callbacks, and is responsible for producing an output file.

Runners should be idempotent per (inputs, params). Implementations typically
wrap an upstream repo's inference code as a subprocess or import.
"""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vidify.specs.schema import ModelSpec


@dataclass
class JobContext:
    job_id: str
    spec: ModelSpec
    inputs: dict[str, Path | str]
    params: dict[str, Any]
    output_path: Path
    weights_dir: Path
    scratch_dir: Path
    logs: list[str] = field(default_factory=list)
    progress_cb: Callable[[float, str], None] | None = None

    def log(self, msg: str) -> None:
        self.logs.append(msg)

    def progress(self, fraction: float, msg: str = "") -> None:
        if self.progress_cb:
            self.progress_cb(fraction, msg)


class Runner(ABC):
    """Base class every model runner inherits from."""

    spec: ModelSpec

    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec

    @abstractmethod
    def run(self, ctx: JobContext) -> Path:
        """Execute inference and return the path to the produced output file."""


def load_runner(spec: ModelSpec) -> Runner:
    """Resolve ``spec.runner`` (dotted path) into a Runner instance."""
    module_path, _, class_name = spec.runner.partition(":")
    if not module_path or not class_name:
        raise ValueError(f"bad runner spec: {spec.runner!r}; expected 'pkg.mod:Class'")
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(spec)
