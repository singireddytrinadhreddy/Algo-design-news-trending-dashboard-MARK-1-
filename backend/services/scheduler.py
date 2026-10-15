from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings
from backend.database import SessionLocal
from backend.models import Source
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

    db = SessionLocal()
    try:
        enabled_sources = db.query(Source).filter(Source.is_enabled == True).all()
        base_time = datetime.now()
        stagger_step_sec = 10

        for idx, src in enumerate(enabled_sources):
            interval_min = src.fetch_interval_min or (15 if src.source_category == "A" else 60)
            start_date = base_time + timedelta(seconds=idx * stagger_step_sec)
            job_id = f"fetch_{src.slug}"
            scheduler.add_job(
                job_fetch_source,
                trigger=IntervalTrigger(minutes=interval_min, start_date=start_date),
                args=[src.slug],
                id=job_id,
                replace_existing=True
            )
            print(f"[Scheduler] Registered '{src.slug}' (Cat {src.source_category}) every {interval_min}m, starting at {start_date.strftime('%H:%M:%S')}")

        # Periodic AI Sweep (staggered after source fetches start)
        ai_start_date = base_time + timedelta(seconds=max(1, len(enabled_sources)) * stagger_step_sec + 5)
        scheduler.add_job(
            job_ai_sweep,
            trigger=IntervalTrigger(minutes=5, start_date=ai_start_date),
            id="ai_sweep",
            replace_existing=True
        )
        print(f"[Scheduler] Registered AI sweep every 5m, starting at {ai_start_date.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[Scheduler] Error configuring sources from DB: {e}")
    finally:
        db.close()

    scheduler.start()
    print("[Scheduler] APScheduler background jobs started.")

def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] APScheduler stopped.")
