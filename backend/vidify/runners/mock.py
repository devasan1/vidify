"""CPU-only mock runner — animates an image + audio via ffmpeg filters.

Produces a real MP4 so the full UI/pipeline works on a box with no GPU.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from vidify.runners.base import JobContext, Runner


def _run(cmd: list[str], ctx: JobContext) -> None:
    ctx.log("$ " + " ".join(str(c) for c in cmd))
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout:
        ctx.log(proc.stdout)
    if proc.stderr:
        ctx.log(proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {cmd[0]}")


class MockRunner(Runner):
    def run(self, ctx: JobContext) -> Path:
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is required for the mock runner")

        image = Path(ctx.inputs["image"])
        audio = Path(ctx.inputs["audio"])
        fps = int(ctx.params.get("fps", 25))
        zoom = float(ctx.params.get("zoom", 1.1))

        ctx.progress(0.05, "Probing audio duration…")
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                str(audio),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration = float(probe.stdout.strip() or "3")
        total_frames = max(int(duration * fps), 1)

        ctx.progress(0.2, f"Rendering {total_frames} frames at {fps}fps…")
        output = ctx.output_path
        output.parent.mkdir(parents=True, exist_ok=True)

        # Slow zoom + loop the still image for the audio duration, then mux audio.
        _run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(image),
                "-i",
                str(audio),
                "-filter_complex",
                f"[0:v]scale=1280:-2,zoompan=z='min(zoom+0.0015,{zoom})':d={total_frames}"
                f":s=1280x720:fps={fps}[v]",
                "-map",
                "[v]",
                "-map",
                "1:a",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output),
            ],
            ctx,
        )
        ctx.progress(1.0, "Done")
        return output
