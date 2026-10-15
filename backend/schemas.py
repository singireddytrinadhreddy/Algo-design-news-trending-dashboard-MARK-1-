from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

# ============================================================
# Source Schemas
# ============================================================

class SourceResponse(BaseModel):
    id: int
    slug: str
    display_name: str
    source_category: str = Field(..., description="'A' for Direct Platform API, 'B' for Derived/Journalistic Signal")
    source_type_label: str = Field(..., description="E.g. 'Official API', 'Search Interest', 'News Coverage'")
    icon_filename: str | None = None
    is_enabled: bool
    fetch_interval_min: int

    class Config:
        from_attributes = True

class LastFetchInfo(BaseModel):
    status: str
    items_fetched: int
    items_new: int
    duration_ms: int
    completed_at: datetime | None = None
    error_message: str | None = None

class SourceStatusResponse(BaseModel):
    id: int
    slug: str
    display_name: str
    source_category: str
    source_type_label: str
    icon_filename: str | None = None
    is_enabled: bool
    fetch_interval_min: int
    last_fetch: LastFetchInfo | None = None
    total_items_24h: int = 0

    class Config:
        from_attributes = True

class SourceListResponse(BaseModel):
    total_sources: int
    sources: list[SourceResponse]


# ============================================================
# Category Schemas
# ============================================================

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str | None = None
    item_count: int = 0

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    total_categories: int
    categories: list[CategoryResponse]


# ============================================================
# Engagement & Trending Item Schemas
# ============================================================

class EngagementMetric(BaseModel):
    value: int | None = None
    label: str | None = None

class TrendRegion(BaseModel):
    label: str
    scope: str  # "local" | "country" | "global"
    basis: str

class TrendItemResponse(BaseModel):
    id: int
    source_id: int
    external_id: str
    title: str
    description: str | None = None
    url: str
    thumbnail_url: str | None = None
    author: str | None = None
    engagement: EngagementMetric
    secondary_engagement: EngagementMetric | None = None
    rank: int | None = None
    region: str = "global"
    trending_region: TrendRegion | None = None
    source_category: str = Field(..., description="'A' = Direct API, 'B' = Derived Signal")
    published_at: datetime | None = None
    fetched_at: datetime
    category: CategoryResponse | None = None
    ai_summary: str | None = None
    location_india: str | None = None
    ai_processed: bool = False
    raw_json: str | None = None
    source: SourceResponse

    class Config:
        from_attributes = True

class FilterMetadata(BaseModel):
    source: list[str] | None = None
    source_category: str | None = None
    recency: str = "24h"
    region_scope: str | None = None
    category: str | None = None
    sort: str = "recency"

class TrendListResponse(BaseModel):
    items: list[TrendItemResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    filters_applied: FilterMetadata


# ============================================================
# Pipeline & System Schemas
# ============================================================

class PipelineFetchSummary(BaseModel):
    source_slug: str
    status: str
    items_fetched: int
    items_new: int
    duration_ms: int
    error_message: str | None = None

class PipelineRunResponse(BaseModel):
    status: str
    message: str
    total_sources_attempted: int
    total_items_fetched: int
    total_items_new: int
    details: list[PipelineFetchSummary]

class PipelineStatusResponse(BaseModel):
    is_running: bool = False
    last_run_time: datetime | None = None
    total_items_in_db: int = 0
    total_ai_processed: int = 0
    total_ai_pending: int = 0
    mock_fetch_mode: bool = True
    mock_ai_mode: bool = True
    active_sources_count: int = 0

class AIProcessResponse(BaseModel):
    status: str
    items_processed: int
    items_succeeded: int
    items_failed: int
    mock_mode: bool

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    mock_fetch_mode: bool
    mock_ai_mode: bool
    database_connected: bool
    sources_enabled: int
