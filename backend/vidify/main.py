"""FastAPI application factory and uvicorn entrypoint."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vidify import __version__
from vidify.api.routes_health import router as health_router
from vidify.api.routes_jobs import router as jobs_router
from vidify.api.routes_models import router as models_router
from vidify.api.routes_settings import router as settings_router
from vidify.api.routes_specs import router as specs_router
from vidify.config import SETTINGS

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vidify",
        description="Local open-source AI video studio",
        version=__version__,
    )

    # CORS — only needed in dev when frontend runs on a different port.
    if SETTINGS.dev_mode:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health_router)
    # routes_models exposes /api/models/installed — must be registered BEFORE
    # routes_specs' /api/models/{model_id} so FastAPI matches the literal path first.
    app.include_router(models_router)
    app.include_router(specs_router)
    app.include_router(jobs_router)
    app.include_router(settings_router)

    # Serve produced outputs directly for <video> tags in the UI.
    app.mount("/outputs", StaticFiles(directory=str(SETTINGS.outputs_dir)), name="outputs")

    # Serve the built frontend, if present (production mode). The SPA uses
    # client-side routing, so unknown paths must fall back to index.html.
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=str(assets_dir)),
                name="assets",
            )

        index_file = frontend_dist / "index.html"

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa_fallback(full_path: str) -> FileResponse:
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404)
            candidate = frontend_dist / full_path
            if full_path and candidate.is_file():
                return FileResponse(str(candidate))
            return FileResponse(str(index_file))

    return app


app = create_app()


def main() -> None:
    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    uvicorn.run(
        "vidify.main:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        reload=SETTINGS.dev_mode,
    )


if __name__ == "__main__":
    main()
