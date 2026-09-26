from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Source, FetchLog, TrendingItem
from backend.schemas import (
    SourceListResponse, SourceResponse, SourceStatusResponse, LastFetchInfo
)

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])

@router.get("", response_model=SourceListResponse)
def list_sources(db: Session = Depends(get_db)):
    """Retrieve all available data sources with their category and enablement status."""
    sources = db.query(Source).order_by(Source.source_category.asc(), Source.id.asc()).all()
    return SourceListResponse(
        total_sources=len(sources),
        sources=[SourceResponse.model_validate(s) for s in sources]
    )

@router.get("/{slug}/status", response_model=SourceStatusResponse)
def get_source_status(slug: str, db: Session = Depends(get_db)):
    """Retrieve detailed operational status, latest fetch log, and 24-hour item volume for a source."""
    source = db.query(Source).filter(Source.slug == slug).first()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source with slug '{slug}' not found.")

    # Get latest fetch log
    latest_log = db.query(FetchLog).filter(
        FetchLog.source_id == source.id
    ).order_by(FetchLog.started_at.desc()).first()

    last_fetch = None
    if latest_log:
        last_fetch = LastFetchInfo(
            status=latest_log.status,
            items_fetched=latest_log.items_fetched,
            items_new=latest_log.items_new,
            duration_ms=latest_log.duration_ms,
            completed_at=latest_log.completed_at,
            error_message=latest_log.error_message
        )

    # Calculate items in past 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    total_24h = db.query(TrendingItem).filter(
        TrendingItem.source_id == source.id,
        TrendingItem.fetched_at >= cutoff
    ).count()

    return SourceStatusResponse(
        id=source.id,
        slug=source.slug,
        display_name=source.display_name,
        source_category=source.source_category,
        source_type_label=source.source_type_label,
        icon_filename=source.icon_filename,
        is_enabled=source.is_enabled,
        fetch_interval_min=source.fetch_interval_min,
        last_fetch=last_fetch,
        total_items_24h=total_24h
    )
