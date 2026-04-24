#!/usr/bin/env python3
"""CLI-friendly bulk model downloader.

Examples:
    python scripts/download_models.py --list
    python scripts/download_models.py musetalk wav2lip
    python scripts/download_models.py --category talking-head
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from vidify.downloader import check_installed, download_model  # noqa: E402
from vidify.specs import REGISTRY, get_category, get_model, list_models  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Vidify model weights.")
    parser.add_argument("models", nargs="*", help="Model IDs to download.")
    parser.add_argument("--list", action="store_true", help="List all known models and exit.")
    parser.add_argument("--category", help="Download every model in this category.")
    parser.add_argument(
        "--skip-installed",
        action="store_true",
        default=True,
        help="Skip models that are already installed (default).",
    )
    args = parser.parse_args()

    if args.list:
        for m in sorted(REGISTRY.values(), key=lambda s: (s.category.value, s.name)):
            state = check_installed(m)
            marker = "✓" if state.status.value == "installed" else "·"
            print(f"  {marker} {m.id:<28} {m.category.value:<22} {m.name}")
        return 0

    targets = []
    if args.category:
        cat = get_category(args.category)
        if cat is None:
            print(f"unknown category: {args.category}", file=sys.stderr)
            return 2
        targets.extend(list_models(cat))
    for model_id in args.models:
        spec = get_model(model_id)
        if spec is None:
            print(f"unknown model: {model_id}", file=sys.stderr)
            return 2
        targets.append(spec)

    if not targets:
        parser.print_help()
        return 1

    # De-dup while preserving order.
    seen = set()
    dedup = []
    for s in targets:
        if s.id in seen:
            continue
        seen.add(s.id)
        dedup.append(s)

    for spec in dedup:
        state = check_installed(spec)
        if args.skip_installed and state.status.value == "installed":
            print(f"[=] {spec.id} already installed ({state.size_gb} GB)")
            continue
        print(f"[↓] {spec.id}: {spec.name}")

        last_msg = ""

        def cb(frac: float, msg: str) -> None:
            nonlocal last_msg
            if msg and msg != last_msg:
                print(f"    [{int(frac*100):3d}%] {msg}")
                last_msg = msg

        state = download_model(spec, progress_cb=cb)
        if state.status.value == "installed":
            print(f"[✓] {spec.id} → {state.path}  ({state.size_gb} GB)")
        else:
            print(f"[✗] {spec.id}: {state.message}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
