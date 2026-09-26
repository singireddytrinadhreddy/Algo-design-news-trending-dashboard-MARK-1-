from backend.routers.trends import router as trends_router
from backend.routers.sources import router as sources_router
from backend.routers.categories import router as categories_router
from backend.routers.pipeline import router as pipeline_router

__all__ = [
    "trends_router",
    "sources_router",
    "categories_router",
    "pipeline_router"
]
