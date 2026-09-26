import json
from datetime import datetime
from typing import Any
import httpx

from backend.config import settings
from backend.fetchers.base import AbstractFetcher, TrendingItemCreate

class YouTubeFetcher(AbstractFetcher):
    slug = "youtube"
    source_category = "A"

    async def fetch_raw(self) -> list[dict]:
        """Fetch most popular videos via YouTube Data API v3."""
        if not settings.YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY is not configured.")

        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": "IN",
            "maxResults": 50,
            "key": settings.YOUTUBE_API_KEY
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])

    def normalize(self, raw_items: list[dict]) -> list[TrendingItemCreate]:
        items: list[TrendingItemCreate] = []
        for rank, raw in enumerate(raw_items, start=1):
            vid_id = raw.get("id") or str(raw.get("etag", ""))
            snippet = raw.get("snippet", {})
            stats = raw.get("statistics", {})

            title = snippet.get("title", "").strip()
            if not title:
                continue

            desc = snippet.get("description", "")
            channel = snippet.get("channelTitle", "Unknown Channel")
            thumb = snippet.get("thumbnails", {}).get("high", {}).get("url") or snippet.get("thumbnails", {}).get("default", {}).get("url")

            # Parse publication date
            pub_str = snippet.get("publishedAt")
            published_at = None
            if pub_str:
                try:
                    published_at = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                except Exception:
                    pass

            views = None
            if "viewCount" in stats:
                try:
                    views = int(stats["viewCount"])
                except (ValueError, TypeError):
                    pass

            comments = None
            if "commentCount" in stats:
                try:
                    comments = int(stats["commentCount"])
                except (ValueError, TypeError):
                    pass

            item = TrendingItemCreate(
                external_id=str(vid_id),
                title=title,
                description=desc[:600] if desc else None,
                url=f"https://www.youtube.com/watch?v={vid_id}",
                thumbnail_url=thumb,
                author=channel,
                engagement_value=views,
                engagement_label="views",
                secondary_value=comments,
                secondary_label="comments",
                rank=rank,
                region="US",
                published_at=published_at,
                raw_json=json.dumps(raw)
            )
            items.append(item)
        return items
