"""``vidify`` command-line entrypoint.

Two subcommands:

* ``vidify serve`` — start the backend (uvicorn).
* ``vidify download <model>`` — fetch a model's weights to the Vidify cache.
"""

from __future__ import annotations

import typer

from vidify.config import SETTINGS
from vidify.downloader import check_installed, download_model, remove_model
from vidify.specs import get_model, list_categories, list_models
from vidify.specs.schema import CATEGORY_META

app = typer.Typer(add_completion=False, help="Vidify — local open-source AI video studio")


@app.command()
def serve(
    host: str = typer.Option(None, "--host", help="Override VIDIFY_HOST."),
    port: int = typer.Option(None, "--port", help="Override VIDIFY_PORT."),
    dev: bool = typer.Option(False, "--dev", help="Run in dev mode (reload, CORS)."),
) -> None:
    """Start the Vidify backend server."""
    import os

    import uvicorn

    if host:
        os.environ["VIDIFY_HOST"] = host
    if port:
        os.environ["VIDIFY_PORT"] = str(port)
    if dev:
        os.environ["VIDIFY_DEV"] = "1"

    # Reload settings after env changes.
    from importlib import reload

    import vidify.config as cfg

    reload(cfg)

    uvicorn.run(
        "vidify.main:app",
        host=cfg.SETTINGS.host,
        port=cfg.SETTINGS.port,
        reload=cfg.SETTINGS.dev_mode,
    )


@app.command(name="list")
def list_cmd(
    category: str | None = typer.Option(None, "--category", "-c"),
) -> None:
    """List available models, optionally filtered by category."""
    if category:
        from vidify.specs import get_category

        cat = get_category(category)
        if cat is None:
            typer.secho(f"unknown category: {category}", fg=typer.colors.RED, err=True)
            raise typer.Exit(2)
        models = list_models(cat)
    else:
        models = list_models()

    if not models:
        typer.echo("no models")
        return

    for m in models:
        state = check_installed(m)
        marker = "✓" if state.status.value == "installed" else " "
        size = f" [{state.size_gb} GB]" if state.size_gb else ""
        typer.echo(f" {marker} {m.id:<28} {m.category.value:<22} {m.name}{size}")


@app.command()
def categories() -> None:
    """List all categories."""
    for cat in list_categories():
        meta = CATEGORY_META.get(cat, {})
        n = len(list_models(cat))
        typer.echo(f"  {cat.value:<22} {n:>3} models   {meta.get('subtitle', '')}")


@app.command()
def download(
    model_id: str = typer.Argument(..., help="Model id, e.g. 'musetalk'."),
) -> None:
    """Download a model's weights."""
    spec = get_model(model_id)
    if spec is None:
        typer.secho(f"unknown model: {model_id}", fg=typer.colors.RED, err=True)
        raise typer.Exit(2)
    if not spec.weights:
        typer.echo(f"{model_id} has no external weights.")
        return

    typer.echo(f"Downloading {spec.name} to {SETTINGS.models_dir} ...")
    last_msg = ""

    def cb(frac: float, msg: str) -> None:
        nonlocal last_msg
        if msg and msg != last_msg:
            typer.echo(f"  [{int(frac*100):3d}%] {msg}")
            last_msg = msg

    state = download_model(spec, progress_cb=cb)
    if state.status.value == "installed":
        typer.secho(f"installed → {state.path}  ({state.size_gb} GB)", fg=typer.colors.GREEN)
    else:
        typer.secho(f"failed: {state.message}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def remove(model_id: str) -> None:
    """Delete a model's downloaded weights."""
    spec = get_model(model_id)
    if spec is None:
        typer.secho(f"unknown model: {model_id}", fg=typer.colors.RED, err=True)
        raise typer.Exit(2)
    remove_model(spec)
    typer.secho("removed", fg=typer.colors.YELLOW)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
