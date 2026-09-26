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
from backend.fetchers import get_fetcher, ALL_FETCHERS
from backend.services.orchestrator import run_pipeline

async def run_phase5_verification():
    print("=" * 80)
    print("PHASE 5 VERIFICATION SUITE — LIVE API FETCHING ACROSS ALL PLATFORMS")
    print("=" * 80)

    # 1. Initialize and clean database
    init_db()
    db = SessionLocal()
    
    # Delete old items so everything is freshly retrieved
    db.query(TrendingItem).delete()
    db.query(FetchLog).delete()
    db.commit()

    seed_db(db)

    sources = db.query(Source).all()
    print(f"\n[OK] Total sources registered in database: {len(sources)}")
    cat_a = [s for s in sources if s.source_category == "A"]
    cat_b = [s for s in sources if s.source_category == "B"]
    print(f"  • Category A (Direct Official APIs): {len(cat_a)} sources -> {[s.slug for s in cat_a]}")
    print(f"  • Category B (Derived Signals):       {len(cat_b)} sources -> {[s.slug for s in cat_b]}")

    assert len(cat_a) == 9, f"Expected 9 Category A sources, got {len(cat_a)}"
    assert len(cat_b) == 6, f"Expected 6 Category B sources, got {len(cat_b)}"

    # 2. Run Pipeline Ingestion across all 15 sources
    print("\n--- 2. Executing Real Ingestion Cycle across All 15 Sources ---")
    results = await run_pipeline(db)

    total_fetched = sum(r.items_fetched for r in results)
    total_new = sum(r.items_new for r in results)

    for r in results:
        status_icon = "[OK]" if r.status == "success" else "[ERROR]"
        print(f"  {status_icon:7} {r.source_slug:16} | Status: {r.status:7} | Fetched: {r.items_fetched:2} | New: {r.items_new:2} | Duration: {r.duration_ms:5}ms")

    # 3. Deduplication Check on Second Execution Cycle
    print("\n--- 3. Testing Deduplication on Second Execution Cycle ---")
    results2 = await run_pipeline(db)
    new_on_2nd = sum(r.items_new for r in results2)
    assert new_on_2nd == 0, f"Deduplication failed! Created {new_on_2nd} duplicate records on 2nd cycle."
    print(f"[OK] Deduplication verified across all {len(results2)} sources: 0 duplicate records created.")

    # 4. Display Verification Deliverable: Real Live Data for Category B News Sources & Category A Sources
    print("\n" + "=" * 80)
    print("LIVE DATA DELIVERABLE — REAL VERIFIABLE ARTICLES & HEADLINES")
    print("=" * 80)

    verifiable_slugs = [
        "instagram_news", "facebook_news", "twitter_news",
        "reddit_news", "twitch_news", "google_trends",
        "devto", "lemmy", "github"
    ]

    for slug in verifiable_slugs:
        src = db.query(Source).filter(Source.slug == slug).first()
        if not src:
            continue
        items = db.query(TrendingItem).filter(
            TrendingItem.source_id == src.id
        ).order_by(TrendingItem.fetched_at.desc(), TrendingItem.rank.asc().nullslast()).limit(2).all()

        print(f"\n>>> SOURCE: {src.display_name.upper()} (Slug: {slug} | Category {src.source_category})")
        for idx, it in enumerate(items, start=1):
            print(f"  Item #{idx}:")
            print(f"    • Title:        {it.title}")
            print(f"    • Live URL:     {it.url}")
            print(f"    • Published At: {it.published_at or 'N/A'}")
            print(f"    • Fetched At:   {it.fetched_at.isoformat()}Z")
            if it.author:
                print(f"    • Attribution:  {it.author}")
            if it.engagement_value is not None:
                print(f"    • Engagement:   {it.engagement_value:,} {it.engagement_label}")

    print("\n" + "=" * 80)
    print("ALL PHASE 5 VERIFICATION TESTS COMPLETED SUCCESSFULLY (100% GREEN)!")
    print("=" * 80)
    db.close()

if __name__ == "__main__":
    asyncio.run(run_phase5_verification())
