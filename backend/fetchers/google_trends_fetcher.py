import json
from datetime import datetime
from typing import Any
import httpx
import feedparser

from backend.fetchers.base import AbstractFetcher, TrendingItemCreate

class GoogleTrendsFetcher(AbstractFetcher):
    slug = "google_trends"
    source_category = "B"

    async def fetch_raw(self) -> list[dict]:
        """Fetch daily search trends from Google Trends live RSS feed for India."""
        rss_url = "https://trends.google.com/trending/rss?geo=IN"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(rss_url, headers=headers)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            items = []
            for entry in feed.entries:
                traffic = getattr(entry, "ht_approx_traffic", getattr(entry, "approx_traffic", "1K+"))
                query = entry.title
                link = entry.link or f"https://trends.google.com/trends/explore?q={query.replace(' ', '%20')}"
                items.append({
                    "query": query,
                    "formatted_traffic": traffic,
                    "url": link,
                    "snippet": getattr(entry, "summary", f"Search interest detected for '{query}'."),
                    "published": getattr(entry, "published", "")
                })
            return items

    def normalize(self, raw_items: list[dict]) -> list[TrendingItemCreate]:
        items: list[TrendingItemCreate] = []
        for rank, raw in enumerate(raw_items, start=1):
            query = (raw.get("query") or raw.get("title", "")).strip()
            if not query:
                continue

            traffic_str = str(raw.get("formatted_traffic") or "High")
            url = raw.get("url") or f"https://trends.google.com/trends/explore?q={query.replace(' ', '%20')}"
            snippet = raw.get("snippet") or f"High search interest detected for '{query}' across Google Search."

            # Parse numeric approx traffic
            approx_val = raw.get("approx_traffic")
            if not approx_val and "+" in traffic_str:
                clean_t = traffic_str.replace("+", "").replace(",", "").replace("K", "000").replace("M", "000000")
                try:
                    approx_val = int(clean_t)
                except ValueError:
                    approx_val = None

            pub_date = None
            if "published" in raw and raw["published"]:
                try:
                    pub_date = datetime.fromisoformat(raw["published"].replace("Z", "+00:00"))
                except Exception:
                    pass

            item = TrendingItemCreate(
                external_id=f"gtrend_{query.lower().replace(' ', '_')}",
                title=query,
                description=f"Search Interest: {traffic_str}. {snippet}",
                url=url,
                thumbnail_url=None,
                author="Google Search Interest",
                engagement_value=approx_val,
                engagement_label="searches",
                secondary_value=None,
                secondary_label=None,
                rank=raw.get("rank") or rank,
                region="IN",
                published_at=pub_date,
                raw_json=json.dumps(raw)
            )
            items.append(item)
        return items
