import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import engine, SessionLocal
from backend.seed import init_db, seed_db
from backend.models import TrendingItem, Source
from backend.schemas import HealthResponse
from backend.services.orchestrator import run_pipeline
from backend.services.ai_processor import process_unprocessed_items
from backend.services.scheduler import start_scheduler, stop_scheduler
from backend.routers import (
    trends_router, sources_router, categories_router, pipeline_router
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Initialize and seed database
    init_db()
    db = SessionLocal()
    try:
        seed_db(db)

        # Cold start check: if 0 items in DB, run initial ingestion sweep
        items_count = db.query(TrendingItem).count()
        if items_count == 0:
            print("[Startup] Database has 0 items. Running initial cold-start fetch sweep...")
            await run_pipeline(db, force_live=False)
            await process_unprocessed_items(db, limit=100)
            print(f"[Startup] Ingestion completed. DB now contains {db.query(TrendingItem).count()} items.")
    finally:
        db.close()

    # 2. Start APScheduler background jobs
    start_scheduler()

    yield

    # 3. Shutdown
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(trends_router)
app.include_router(sources_router)
app.include_router(categories_router)
app.include_router(pipeline_router)

# Mount static frontend directory if it exists
if not FRONTEND_DIR.exists():
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """System health check endpoint."""
    db = SessionLocal()
    sources_enabled = 0
    db_connected = False
    try:
        sources_enabled = db.query(Source).filter(Source.is_enabled == True).count()
        db_connected = True
    except Exception:
        db_connected = False
    finally:
        db.close()

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        mock_fetch_mode=settings.MOCK_FETCH_MODE,
        mock_ai_mode=settings.MOCK_AI_MODE,
        database_connected=db_connected,
        sources_enabled=sources_enabled
    )

@app.get("/", tags=["system"])
def read_root():
    """Serve frontend index.html if present, else return API root info."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_v1": {
            "trends": "/api/v1/trends",
            "sources": "/api/v1/sources",
            "categories": "/api/v1/categories",
            "pipeline": "/api/v1/pipeline/status"
        }
    })
