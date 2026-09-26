import json
import logging
import time
from typing import Any
import google.generativeai as genai
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import TrendingItem, Category
from backend.utils.rate_limiter import gemini_rate_limiter
from backend.services.mock_ai import get_mock_ai_summary, detect_indian_location_heuristic, classify_category_heuristic

logger = logging.getLogger("socialpulse.ai_processor")

PREFERRED_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.7-flash",
    "gemini-3.6-flash"
]

def clean_json_response(raw_text: str) -> str:
    """Strip markdown code fence wrappers from raw LLM output if present."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_trend_with_gemini(
    title: str,
    description: str = "",
    platform_name: str = "",
    source_category: str = "A"
) -> dict[str, Any]:
    """
    Execute a structured Gemini AI call to generate:
    1. 'summary': 1-2 concise sentences explaining why this topic is trending.
    2. 'category': Standardized category name.
    3. 'location_india': Specific Indian city/district/state ONLY if genuinely identifiable in the content, null otherwise.
    4. 'is_platform_trend': True if genuinely about platform trends/creators, false if off-topic general news.
    """
    if settings.MOCK_AI_MODE or not settings.GEMINI_KEY:
        summary_text, cat_name, loc_india, is_trend = get_mock_ai_summary(platform_name.lower().replace(" ", "_"), title, description)
        return {
            "summary": summary_text,
            "category": cat_name,
            "location_india": loc_india,
            "is_platform_trend": is_trend,
            "success": True
        }

    try:
        genai.configure(api_key=settings.GEMINI_KEY)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        cat = classify_category_heuristic(f"{title} {description}", default_source=platform_name)
        loc = detect_indian_location_heuristic(f"{title} {description}")
        return {
            "summary": "[AI Analysis Unavailable: Failed to configure Gemini API key.]",
            "category": cat,
            "location_india": loc,
            "is_platform_trend": True,
            "success": False
        }

    # Enforce sliding-window rate limit (10 RPM)
    gemini_rate_limiter.acquire()

    cat_list_str = ", ".join([c["name"] for c in settings.CATEGORIES])
    cat_type_desc = "first-party live platform trend" if source_category == "A" else "verified third-party news coverage regarding social media trends"

    prompt = f"""You are SocialPulse AI, an expert social media trending intelligence engine.
Analyze the following {cat_type_desc} from {platform_name} and return ONLY a valid JSON object matching this schema:

{{
  "summary": "1-2 concise, factual sentences explaining why this topic is trending, the core context, and why users or developers are engaging with it.",
  "category": "Must be exactly one of: {cat_list_str}",
  "location_india": "Specific Indian city, district, or state as a string (e.g. 'Bengaluru, Karnataka', 'Mumbai', 'Kerala', 'India') ONLY if the story/topic genuinely and physically occurred in or directly targets that specific locality. If it is a nationwide Indian story without a specific local event, return 'India'. If international/global, return null. NEVER return a boolean.",
  "is_platform_trend": true or false (return true if this story is genuinely about a trending topic, viral post, creator discussion, or community event relating to {platform_name}; return false if it is off-topic general news, unrelated politics, or purely corporate financial filings)
}}

CRITICAL ACCURACY & CATEGORIZATION RULES:
1. UNVERIFIED CLAIMS & HEDGING: If the headline, source, or context contains hedging words such as 'alleged', 'unverified', 'claims', 'reportedly', 'according to a viral post', 'rumored', or refers to an anonymous social media claim (e.g. from Reddit, X, etc.) that lacks official verification, YOUR SUMMARY MUST EXPLICITLY PRESERVE THIS UNCERTAINTY. Use phrases like 'According to unverified social media claims...', 'Reportedly...', or 'An alleged claim that...'. NEVER present unconfirmed viral claims or rumors as established flat facts.
2. CREATOR & STREAMING CONTENT: Categorize video creators, streamers, Twitch drama, and gaming content as 'Gaming' or 'Entertainment'. NEVER categorize creator drama, bullying, or streaming spats as 'Health'.
3. NO GENERIC BOILERPLATE: Write unique, insightful 1-2 sentence explanations specific to the actual headline and details provided. Do not use generic template phrases like 'Major trending story centered in...'.

Platform: {platform_name}
Title/Headline: {title}
Context/Description: {description[:1200]}
"""

    last_error = ""
    # Try models in preference order (e.g. fallback from quota-limited model to available model)
    for model_name in PREFERRED_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            raw_text = response.text
            cleaned = clean_json_response(raw_text)
            data = json.loads(cleaned)

            summary = data.get("summary", "").strip()
            category = data.get("category", "Technology").strip()
            location_india = data.get("location_india")
            is_platform_trend = data.get("is_platform_trend", True)

            if not summary:
                summary = f"Trending on {platform_name} with high community engagement and discussions."

            # Validate location_india is a string or None (not boolean or placeholder)
            if location_india is not None:
                if isinstance(location_india, bool):
                    location_india = "India" if location_india else None
                elif isinstance(location_india, str):
                    if location_india.lower() in ["null", "none", "n/a", "global", "false"]:
                        location_india = None
                    elif location_india.lower() == "true":
                        location_india = "India"
                else:
                    location_india = None

            # If Gemini missed a clearly identifiable Indian city/state in text, apply heuristic
            if not location_india:
                location_india = detect_indian_location_heuristic(f"{title} {description}")

            return {
                "summary": summary,
                "category": category,
                "location_india": location_india.strip() if location_india else None,
                "is_platform_trend": bool(is_platform_trend),
                "success": True
            }

        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "404" in last_error or "503" in last_error:
                logger.warning(f"Model '{model_name}' failed ({last_error[:80]}). Trying next preferred model...")
                continue
            logger.error(f"Gemini API error with '{model_name}' for '{title[:35]}': {e}")
            continue

    # Honest failure reporting — NO silent fallback to generic mock templates when in live mode!
    cat_fallback = classify_category_heuristic(f"{title} {description}", default_source=platform_name)
    loc_fallback = detect_indian_location_heuristic(f"{title} {description}")
    
    error_summary = f"[AI Analysis Temporarily Unavailable: Gemini API rate limit or service error. Will automatically retry on next pipeline run.]"
    return {
        "summary": error_summary,
        "category": cat_fallback,
        "location_india": loc_fallback,
        "is_platform_trend": True,
        "success": False
    }

async def process_unprocessed_items(db: Session, limit: int = 50) -> tuple[int, int, int]:
    """
    Process un-summarized trending items in batch with Gemini AI or mock fallback.
    Returns: (total_attempted, succeeded, failed)
    """
    items = db.query(TrendingItem).filter(
        TrendingItem.ai_processed == False
    ).limit(limit).all()

    if not items:
        return (0, 0, 0)

    # Pre-cache category names
    all_cats = db.query(Category).all()
    cat_map = {c.name.lower(): c for c in all_cats}
    default_cat = cat_map.get("other") or (all_cats[0] if all_cats else None)

    succeeded = 0
    failed = 0

    for item in items:
        try:
            platform_name = item.source.display_name if item.source else "Social Platform"
            src_cat = item.source_category or "A"

            analysis = analyze_trend_with_gemini(
                title=item.title,
                description=item.description or "",
                platform_name=platform_name,
                source_category=src_cat
            )

            # Strict relevance filter: if Gemini determines an item is off-topic for Category B news, purge it
            if src_cat == "B" and analysis.get("is_platform_trend") is False:
                logger.info(f"Purging off-topic news item: '{item.title[:40]}'")
                db.delete(item)
                succeeded += 1
                continue

            item.ai_summary = analysis.get("summary")
            item.location_india = analysis.get("location_india")

            assigned_cat_name = analysis.get("category", "Technology").lower()
            matched_cat = cat_map.get(assigned_cat_name, default_cat)
            if matched_cat:
                item.category_id = matched_cat.id

            if analysis.get("success", True):
                item.ai_processed = True
                succeeded += 1
            else:
                item.ai_processed = False
                failed += 1

        except Exception as e:
            logger.error(f"Error processing AI for item {item.id}: {e}")
            item.ai_summary = f"[AI Analysis Failed: {e}]"
            item.ai_processed = False
            failed += 1

    db.commit()
    return (len(items), succeeded, failed)
