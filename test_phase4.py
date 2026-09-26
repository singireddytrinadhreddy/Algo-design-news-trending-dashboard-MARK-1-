import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.database import SessionLocal, Base, engine
from backend.seed import init_db, seed_db
from backend.models import TrendingItem, Source, Category, FetchLog
from backend.fetchers import get_fetcher

async def run_phase4_live_verification():
    print("=" * 75)
    print("PHASE 4 VERIFICATION SUITE — TIER 1 LIVE NO-AUTH SOURCES")
    print("=" * 75)

    init_db()
    db = SessionLocal()
    seed_db(db)

    live_slugs = ["hackernews", "mastodon", "bluesky", "wikipedia"]

    # 1. Test Live Fetch for each Tier 1 source
    print("\n--- 1. Executing Live Fetch for Tier 1 Sources (force_live=True) ---")
    live_samples = {}

    for slug in live_slugs:
        fetcher = get_fetcher(slug)
        assert fetcher is not None, f"Fetcher for {slug} not found"

        print(f"\n[Connecting to Live API] {slug}...")
        result = await fetcher.execute(db, force_live=True)

        assert result.status == "success", f"Live fetch failed for {slug}: {result.error_message}"
        assert result.items_fetched > 0, f"No items retrieved from live {slug}"

        print(f"  [SUCCESS] {slug:14} -> Fetched: {result.items_fetched:2} live items | New: {result.items_new:2} | Duration: {result.duration_ms}ms")

        # Query top 2 live items from DB for this source
        src = db.query(Source).filter(Source.slug == slug).first()
        items = db.query(TrendingItem).filter(
            TrendingItem.source_id == src.id
        ).order_by(TrendingItem.fetched_at.desc(), TrendingItem.rank.asc().nullslast()).limit(2).all()

        live_samples[slug] = items

    # 2. Test Deduplication on Live Data
    print("\n\n--- 2. Testing Deduplication on Live Data (Second Consecutive Cycle) ---")
    for slug in live_slugs:
        fetcher = get_fetcher(slug)
        result2 = await fetcher.execute(db, force_live=True)
        assert result2.status == "success"
        assert result2.items_new == 0, f"Deduplication failed for live {slug}: {result2.items_new} new items created on 2nd cycle"
        print(f"  [OK] {slug:14} -> 2nd cycle: 0 duplicate records created.")

    # 3. Test Recency Filtering with Live Data
    print("\n--- 3. Testing Recency Queries with Live Items ---")
    now = datetime.utcnow()
    h24_count = db.query(TrendingItem).filter(
        TrendingItem.fetched_at >= now - timedelta(hours=24)
    ).count()
    print(f"  [OK] Total active items in 24h window: {h24_count}")

    # 4. Display Live Deliverable Data
    print("\n" + "=" * 75)
    print("LIVE DATA DELIVERABLE — REAL ITEMS PULLED FROM 4 TIER-1 SOURCES")
    print("=" * 75)

    for slug in live_slugs:
        items = live_samples[slug]
        print(f"\n>>> SOURCE: {items[0].source.display_name.upper()} (Slug: {slug})")
        for idx, it in enumerate(items, start=1):
            print(f"  Item #{idx}:")
            print(f"    • Title:        {it.title}")
            print(f"    • Live URL:     {it.url}")
            print(f"    • Published At: {it.published_at or 'N/A (Real-time Tag)'}")
            print(f"    • Fetched At:   {it.fetched_at.isoformat()}Z")
            if it.engagement_value is not None:
                print(f"    • Engagement:   {it.engagement_value:,} {it.engagement_label}")

    print("\n" + "=" * 75)
    print("ALL PHASE 4 LIVE INTEGRATION TESTS PASSED (100% GREEN)!")
    print("=" * 75)

    db.close()

if __name__ == "__main__":
    asyncio.run(run_phase4_live_verification())
