from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, comments, tickets

app = FastAPI(title="UniDesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(comments.router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


# Serve the built React SPA when it has been bundled alongside the API
# (the deployment image copies frontend/dist to backend/static). No-op for
# local development and tests, where this directory does not exist, so the
# API's behaviour there is unchanged.
_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if _STATIC_DIR.is_dir():
    _ASSETS_DIR = _STATIC_DIR / "assets"
    if _ASSETS_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        target = (_STATIC_DIR / full_path).resolve()
        if target.is_file() and _STATIC_DIR in target.parents:
            return FileResponse(target)
        # client-side route (e.g. /dashboard, /tickets/5) -> let React Router handle it
        return FileResponse(_STATIC_DIR / "index.html")
