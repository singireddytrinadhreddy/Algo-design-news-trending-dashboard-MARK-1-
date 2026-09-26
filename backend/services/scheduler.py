import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings
from backend.database import SessionLocal
from backend.services.orchestrator import run_pipeline
from backend.services.ai_processor import process_unprocessed_items

scheduler = AsyncIOScheduler()

async def job_fetch_source(slug: str):
    """Periodic job for a single source fetcher."""
    db = SessionLocal()
    try:
        await run_pipeline(db, source_slug=slug)
    except Exception as e:
        print(f"[Scheduler] Error in fetch job for {slug}: {e}")
    finally:
        db.close()

async def job_ai_sweep():
    """Periodic job to process un-summarized items with AI."""
    db = SessionLocal()
    try:
        await process_unprocessed_items(db, limit=50)
    except Exception as e:
        print(f"[Scheduler] Error in AI sweep job: {e}")
    finally:
        db.close()

def start_scheduler():
    """Register all periodic jobs and start the background scheduler."""
    if scheduler.running:
        return

    # Category A Sources (YouTube, Mastodon, Bluesky)
    scheduler.add_job(job_fetch_source, trigger=IntervalTrigger(minutes=15), args=["youtube"], id="fetch_youtube", replace_existing=True)
    scheduler.add_job(job_fetch_source, trigger=IntervalTrigger(minutes=15), args=["mastodon"], id="fetch_mastodon", replace_existing=True)
    scheduler.add_job(job_fetch_source, trigger=IntervalTrigger(minutes=15), args=["bluesky"], id="fetch_bluesky", replace_existing=True)

    # Periodic AI Sweep
    scheduler.add_job(job_ai_sweep, trigger=IntervalTrigger(minutes=5), id="ai_sweep", replace_existing=True)

    scheduler.start()
    print("[Scheduler] APScheduler background jobs started.")

def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] APScheduler stopped.")
