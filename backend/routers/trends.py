import math
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_, and_

from backend.database import get_db
from backend.models import TrendingItem, Source, Category
from backend.schemas import (
    TrendListResponse, TrendItemResponse, EngagementMetric,
    FilterMetadata, CategoryResponse, SourceResponse
)

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])

def format_trend_item(item: TrendingItem) -> TrendItemResponse:
    """Helper to convert SQLAlchemy TrendingItem model to Pydantic TrendItemResponse."""
    cat_response = None
    if item.category:
        cat_response = CategoryResponse(
            id=item.category.id,
            name=item.category.name,
            color=item.category.color,
            item_count=0
        )

    return TrendItemResponse(
        id=item.id,
        source_id=item.source_id,
        external_id=item.external_id,
        title=item.title,
        description=item.description,
        url=item.url,
        thumbnail_url=item.thumbnail_url,
        author=item.author,
        engagement=EngagementMetric(
            value=item.engagement_value,
            label=item.engagement_label
        ),
        secondary_engagement=EngagementMetric(
            value=item.secondary_value,
            label=item.secondary_label
        ) if item.secondary_value is not None else None,
        rank=item.rank,
        region=item.region or "global",
        source_category=item.source_category,
        published_at=item.published_at,
        fetched_at=item.fetched_at,
        category=cat_response,
        ai_summary=item.ai_summary,
        location_india=item.location_india,
        ai_processed=item.ai_processed,
        raw_json=item.raw_json,
        source=SourceResponse.model_validate(item.source)
    )

@router.get("", response_model=TrendListResponse)
def get_trends(
    source: Optional[List[str]] = Query(None, description="Filter by source slug(s), e.g. ?source=youtube&source=reddit"),
    source_category: Optional[str] = Query(None, pattern="^(A|B)$", description="Filter by category type: 'A' (Direct API) or 'B' (Derived Signal)"),
    recency: str = Query("24h", pattern="^(6h|12h|24h|all)$", description="Time window based on best timestamp (6h, 12h, 24h, all)"),
    category: Optional[str] = Query(None, description="Filter by category name (e.g. Technology, Science)"),
    sort: str = Query("recency", pattern="^(recency|engagement)$", description="Sort order: recency (newest) or engagement (highest engagement)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve trending items with dynamic filtering across sources, categories, time recency, and sorting.
    """
    query = db.query(TrendingItem).options(
        joinedload(TrendingItem.source),
        joinedload(TrendingItem.category)
    )

    # 1. Source filtering
    if source:
        # Handle comma-separated slugs if passed as single string
        slugs = []
        for s in source:
            slugs.extend([part.strip() for part in s.split(",") if part.strip()])
        if slugs:
            query = query.join(TrendingItem.source).filter(Source.slug.in_(slugs))

    # 2. Source Category filtering ('A' vs 'B')
    if source_category:
        query = query.filter(TrendingItem.source_category == source_category.upper())

    # 3. Category filtering
    if category:
        query = query.join(TrendingItem.category).filter(func.lower(Category.name) == category.strip().lower())

    # 4. Recency filtering
    now = datetime.utcnow()
    hours_map = {"6h": 6, "12h": 12, "24h": 24}
    if recency in hours_map:
        cutoff = now - timedelta(hours=hours_map[recency])
        # Use COALESCE(published_at, fetched_at)
        query = query.filter(func.coalesce(TrendingItem.published_at, TrendingItem.fetched_at) >= cutoff)

    # 5. Sorting
    if sort == "engagement":
        # Engagement metric descending, nulls last
        query = query.order_by(
            TrendingItem.engagement_value.desc().nullslast(),
            func.coalesce(TrendingItem.published_at, TrendingItem.fetched_at).desc()
        )
    else:
        # Default: recency descending
        query = query.order_by(
            func.coalesce(TrendingItem.published_at, TrendingItem.fetched_at).desc(),
            TrendingItem.rank.asc().nullslast()
        )

    total = query.count()
    total_pages = max(1, math.ceil(total / per_page))
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    formatted_items = [format_trend_item(it) for it in items]

    return TrendListResponse(
        items=formatted_items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        filters_applied=FilterMetadata(
            source=source,
            source_category=source_category,
            recency=recency,
            category=category,
            sort=sort
        )
    )

@router.get("/{item_id}", response_model=TrendItemResponse)
def get_trend_by_id(item_id: int, db: Session = Depends(get_db)):
    """Retrieve full details of a single trending item by its primary ID."""
    item = db.query(TrendingItem).options(
        joinedload(TrendingItem.source),
        joinedload(TrendingItem.category)
    ).filter(TrendingItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"Trending item with ID {item_id} not found.")

    return format_trend_item(item)
