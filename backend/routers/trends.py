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
    FilterMetadata, CategoryResponse, SourceResponse, TrendRegion
)

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])

def resolve_trending_region(item: TrendingItem) -> TrendRegion:
    """
    Resolve trending region with an honest fallback chain:
    1. If location_india is set and not "India" -> label=that value, scope="local", basis="Location detected from the story content".
    2. If location_india == "India" -> label="India", scope="country", basis="Nationwide Indian story".
    3. If the source is queried with an India filter (google_trends, youtube) -> label="India", scope="country", basis="This source is queried for India (geo/region = IN)".
    4. Otherwise -> label="Global", scope="global", basis="No regional filter available for this source".
    """
    loc = (item.location_india or "").strip()
    slug = item.source.slug if item.source else ""

    if loc and loc.lower() != "india":
        return TrendRegion(
            label=loc,
            scope="local",
            basis="Location detected from the story content"
        )

    if loc.lower() == "india":
        return TrendRegion(
            label="India",
            scope="country",
            basis="Nationwide Indian story"
        )

    if slug in ("google_trends", "youtube") or (item.region and item.region.upper() == "IN"):
        return TrendRegion(
            label="India",
            scope="country",
            basis="This source is queried for India (geo/region = IN)"
        )

    return TrendRegion(
        label="Global",
        scope="global",
        basis="No regional filter available for this source"
    )

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
        trending_region=resolve_trending_region(item),
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
    region_scope: Optional[str] = Query(None, pattern="^(all|india|global|local)$", description="Filter by regional scope: 'all', 'india', 'global', 'local'"),
    category: Optional[str] = Query(None, description="Filter by category name (e.g. Technology, Science)"),
    sort: str = Query("recency", pattern="^(recency|engagement)$", description="Sort order: recency (newest) or engagement (highest engagement)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve trending items with dynamic filtering across sources, categories, time recency, and sorting.
    """
    query = db.query(TrendingItem).join(TrendingItem.source).options(
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
            query = query.filter(Source.slug.in_(slugs))

    # 2. Source Category filtering ('A' vs 'B')
    if source_category:
        query = query.filter(TrendingItem.source_category == source_category.upper())

    # 3. Category filtering
    if category:
        query = query.join(TrendingItem.category).filter(func.lower(Category.name) == category.strip().lower())

    # 3b. Region Scope filtering ('india', 'global', 'local')
    if region_scope == "global":
        query = query.filter(
            (TrendingItem.location_india.is_(None) | (TrendingItem.location_india == "")) &
            (~Source.slug.in_(["google_trends", "youtube"])) &
            (TrendingItem.region != "IN")
        )
    elif region_scope == "india":
        query = query.filter(
            ((TrendingItem.location_india.isnot(None)) & (TrendingItem.location_india != "")) |
            Source.slug.in_(["google_trends", "youtube"]) |
            (TrendingItem.region == "IN")
        )
    elif region_scope == "local":
        query = query.filter(
            TrendingItem.location_india.isnot(None),
            TrendingItem.location_india != "",
            func.lower(TrendingItem.location_india) != "india"
        )

    # 4. Recency filtering
    # Chart-style sources (current chart snapshot) base recency on fetched_at.
    # News coverage sources base recency on actual published date (coalesce with fetched_at if missing).
    from sqlalchemy import case
    chart_sources = ["youtube", "google_trends", "mastodon", "bluesky"]
    effective_time = case(
        (Source.slug.in_(chart_sources), TrendingItem.fetched_at),
        else_=func.coalesce(TrendingItem.published_at, TrendingItem.fetched_at)
    )

    now = datetime.utcnow()
    hours_map = {"6h": 6, "12h": 12, "24h": 24}
    if recency in hours_map:
        cutoff = now - timedelta(hours=hours_map[recency])
        recent_query = query.filter(effective_time >= cutoff)
        # If filtering by a specific source resulted in 0 items, relax the recency cutoff so the user always sees content
        if source and recent_query.count() == 0:
            pass
        else:
            query = recent_query

    # 5. Sorting
    if sort == "engagement":
        # Engagement metric descending, nulls last
        query = query.order_by(
            TrendingItem.engagement_value.desc().nullslast(),
            effective_time.desc()
        )
    else:
        # Default: recency descending
        query = query.order_by(
            effective_time.desc(),
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
            region_scope=region_scope,
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
