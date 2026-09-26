import asyncio
import hashlib
import json
import re
from datetime import datetime
from typing import Any
import httpx
import feedparser
import googlenewsdecoder
from bs4 import BeautifulSoup

from backend.config import settings

EXCLUDED_DOMAINS = [
    "x.com", "twitter.com", "instagram.com", "facebook.com",
    "threads.net", "reddit.com", "twitch.tv", "youtube.com", "tiktok.com"
]

EXCLUDED_OUTLETS = [
    "x.com", "twitter", "instagram", "facebook", "reddit", "twitch", "tiktok", "youtube"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

PLATFORM_KEYWORDS: dict[str, list[str]] = {
    "Instagram": ["instagram", "insta", "reel", "reels", "meta"],
    "Facebook": ["facebook", "fb", "meta", "mark zuckerberg"],
    "Twitter": ["x.com", "twitter", "tweet", "tweets", "retweet", "elon musk", "on x", "x user"],
    "X (Twitter)": ["x.com", "twitter", "tweet", "tweets", "retweet", "elon musk", "on x", "x user"],
    "X": ["x.com", "twitter", "tweet", "tweets", "retweet", "elon musk", "on x", "x user"],
    "Twitch": ["twitch", "streamer", "streamers", "livestream", "streaming", "kick", "kai cenat", "speed", "caedrel", "pokimane", "xqc"]
}

TREND_KEYWORDS: list[str] = [
    "trend", "trending", "viral", "buzz", "sparks", "debate", "reacts", "reaction",
    "outcry", "backlash", "video", "clip", "post", "views", "challenge", "shares",
    "internet", "online", "broadcast", "record", "ban", "feature", "algorithm",
    "million", "star", "interview", "fans", "community", "discussions"
]

def is_valid_news_article(url: str, outlet_name: str | None) -> bool:
    """Validate that the item is genuine third-party journalism and not a direct social media post or unresolved redirect."""
    if not url:
        return False
    clean_url = url.lower()
    if any(domain in clean_url for domain in EXCLUDED_DOMAINS):
        return False
    if "news.google.com" in clean_url:
        return False
    if outlet_name and any(out == outlet_name.lower().strip() for out in EXCLUDED_OUTLETS):
        return False
    return True

def is_topically_relevant(title: str, snippet: str, platform_name: str) -> bool:
    """
    Ensure the article is explicitly relevant to the platform and discusses a trend/viral event,
    filtering out general unrelated tech, political, or hospital news.
    """
    text = f"{title} {snippet}"
    if platform_name in ["Twitter", "X (Twitter)", "X"]:
        pattern = r"\b(x|twitter|tweet|tweets|retweet|elon musk|on x)\b"
    elif platform_name == "Instagram":
        pattern = r"\b(instagram|insta|reel|reels|ig|meta)\b"
    elif platform_name == "Facebook":
        pattern = r"\b(facebook|fb|meta|mark zuckerberg)\b"
    elif platform_name == "Twitch":
        pattern = r"\b(twitch|streamer|streamers|livestream|streaming|esports|gaming|broadcast)\b"
    else:
        pattern = rf"\b{re.escape(platform_name.lower())}\b"

    if not re.search(pattern, text, re.IGNORECASE):
        return False

    trend_pattern = r"\b(trend|trending|viral|buzz|sparks|debate|reacts|reaction|outcry|backlash|video|clip|post|views|challenge|shares|internet|online|broadcast|record|ban|feature|algorithm|million|star|interview|fans|community|discussions|lawsuit|terms|feed|grid|update|notes)\b"
    return bool(re.search(trend_pattern, text, re.IGNORECASE))

def generate_news_article_id(url: str) -> str:
    """Generate deterministic 32-character SHA-256 hash of article URL."""
    clean_url = url.strip().lower()
    return hashlib.sha256(clean_url.encode("utf-8")).hexdigest()[:32]

def _sync_decode_url(raw_url: str) -> str:
    try:
        res = googlenewsdecoder.new_decoderv1(raw_url, interval=0.1)
        if isinstance(res, dict) and res.get("status") and res.get("decoded_url"):
            return res["decoded_url"]
    except Exception:
        pass
    return raw_url

async def decode_url_safe(raw_url: str) -> str:
    """Decode Google News redirect URL to direct publisher link with 6.0s timeout."""
    if "/articles/" not in raw_url:
        return raw_url
    try:
        return await asyncio.wait_for(asyncio.to_thread(_sync_decode_url, raw_url), timeout=6.0)
    except Exception:
        return raw_url

async def _scrape_single_source(client: httpx.AsyncClient, outlet_name: str, page_url: str, base_domain: str, platform_name: str) -> list[dict]:
    found = []
    try:
        resp = await client.get(page_url, timeout=6.0)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            href = a["href"]
            if not title or len(title) < 22:
                continue
            if href.startswith("/"):
                href = f"{base_domain}{href}"

            if not is_valid_news_article(href, outlet_name):
                continue

            if not any(k in href for k in ["/news/", "/article/", "/story/", "/streaming/", "/buzz/", "/202"]):
                continue

            if is_topically_relevant(title, "", platform_name):
                found.append({
                    "source": {"name": outlet_name},
                    "author": outlet_name,
                    "title": title,
                    "description": f"Verified report from {outlet_name} covering trending content on {platform_name}.",
                    "url": href,
                    "urlToImage": None,
                    "publishedAt": datetime.utcnow().isoformat() + "Z",
                    "content": title[:200]
                })
                if len(found) >= 4:
                    break
    except Exception as e:
        print(f"[NewsCoverage] Note on {outlet_name}: {e}")
    return found

async def scrape_direct_news_sites(platform_name: str, max_items: int = 5) -> list[dict]:
    """
    Directly scrape curated major Indian journalism sites concurrently as primary sources.
    """
    # Primary Indian outlets for all platforms
    primary_indian_sources = [
        ("India Today", "https://www.indiatoday.in/trending-news", "https://www.indiatoday.in"),
        ("The Indian Express", "https://indianexpress.com/section/trending/", "https://indianexpress.com"),
        ("News18", "https://www.news18.com/buzz/", "https://www.news18.com")
    ]

    sources_to_scrape = list(primary_indian_sources)
    if platform_name == "Twitch":
        sources_to_scrape.append(("Dot Esports", "https://dotesports.com/streaming", "https://dotesports.com"))

    articles: list[dict] = []
    seen_urls: set[str] = set()

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        tasks = [
            _scrape_single_source(client, outlet, url, base, platform_name)
            for outlet, url, base in sources_to_scrape
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                for item in res:
                    u = item.get("url")
                    if u and u not in seen_urls and len(articles) < max_items:
                        seen_urls.add(u)
                        articles.append(item)

    return articles

async def fetch_news_for_platform(platform_name: str, queries: list[str]) -> list[dict]:
    """
    Fetch genuine, published third-party news articles ABOUT platform trends.
    Combines:
    1. Direct scraping of curated Indian news desks (India Today, Indian Express, News18)
    2. Live Google News India RSS with exact-phrase query decoding to direct Indian publisher links
    3. Secondary US fallback (TechCrunch, Social Media Today) only if Indian sources return insufficient results
    All articles are strictly validated for topical relevance and platform domain exclusion.
    """
    articles: list[dict] = []
    seen_urls: set[str] = set()

    # 1. Primary: fetch from direct curated Indian news website scraping
    direct_scraped = await scrape_direct_news_sites(platform_name, max_items=4)
    for art in direct_scraped:
        u = art.get("url")
        if u and u not in seen_urls:
            seen_urls.add(u)
            articles.append(art)

    # 2. Primary Fallback: Live Google News India RSS with Direct Publisher URL Decoding
    if len(articles) < 3:
        for query_item in queries[:2]:
            clean_q = query_item.strip()
            encoded_q = clean_q.replace('"', '%22').replace(" ", "+")
            rss_url = f"https://news.google.com/rss/search?q={encoded_q}+India&hl=en-IN&gl=IN&ceid=IN:en"

            try:
                async with httpx.AsyncClient(headers=HEADERS, timeout=6.0) as client:
                    resp = await client.get(rss_url)
                    if resp.status_code == 200:
                        feed = feedparser.parse(resp.text)
                        for entry in feed.entries[:4]:
                            if len(articles) >= 3:
                                break
                            raw_url = entry.link
                            if not raw_url:
                                continue

                            raw_title = entry.title
                            clean_title = raw_title
                            outlet_name = getattr(entry, "source", {}).get("title")
                            if " - " in raw_title:
                                parts = raw_title.rsplit(" - ", 1)
                                clean_title = parts[0].strip()
                                if not outlet_name:
                                    outlet_name = parts[1].strip()

                            if not outlet_name:
                                outlet_name = "News Outlet"

                            # Quick pre-filter before decoding
                            entry_summary = getattr(entry, "summary", "")
                            if not is_topically_relevant(clean_title, entry_summary, platform_name):
                                continue

                            # Decode Google News link to real publisher link
                            final_url = await decode_url_safe(raw_url)

                            # Strict validation: exclude direct platform posts
                            if not is_valid_news_article(final_url, outlet_name) or final_url in seen_urls:
                                continue

                            seen_urls.add(final_url)
                            articles.append({
                                "source": {"name": outlet_name},
                                "author": outlet_name,
                                "title": clean_title,
                                "description": f"Verified report from {outlet_name} covering trending topics on {platform_name}.",
                                "url": final_url,
                                "urlToImage": None,
                                "publishedAt": datetime.utcnow().isoformat() + "Z",
                                "content": clean_title[:200]
                            })
            except Exception as e:
                print(f"[NewsCoverage] Note on Google News RSS ({platform_name}): {e}")

    # 3. Last Resort Fallback: International desks only if fewer than 3 items found
    if len(articles) < 3:
        fallback_sources = [
            ("TechCrunch", "https://techcrunch.com/category/social/", "https://techcrunch.com"),
            ("Social Media Today", "https://www.socialmediatoday.com/", "https://www.socialmediatoday.com")
        ]
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
            fallback_tasks = [
                _scrape_single_source(client, outlet, url, base, platform_name)
                for outlet, url, base in fallback_sources
            ]
            fallback_results = await asyncio.gather(*fallback_tasks, return_exceptions=True)
            for res in fallback_results:
                if isinstance(res, list):
                    for item in res:
                        u = item.get("url")
                        if u and u not in seen_urls and len(articles) < 4:
                            seen_urls.add(u)
                            articles.append(item)

    return articles
