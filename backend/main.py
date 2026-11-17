import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes import engines, milling
from backend.services.engine_predictor import EngineService
from ml.engines.preprocess import ROOT


@asynccontextmanager
async def lifespan(app):
    app.state.engines = EngineService()
    yield


app = FastAPI(title="DUM-E Intelligence API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(engines.router)
app.include_router(milling.router)


@app.get("/health", tags=["System"])
def health():
    service = app.state.engines
    ready = service.frame is not None and service.artifact is not None
    return {"status": "healthy" if ready else "degraded", "engine_model_loaded": service.artifact is not None,
            "dataset_loaded": service.frame is not None, "milling_model_loaded": False}


# Mount after API routes, keeping /docs and /health available in the single-server build.
dist = ROOT / "frontend/dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="dashboard")
