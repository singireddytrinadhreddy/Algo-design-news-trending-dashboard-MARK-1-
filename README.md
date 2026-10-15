# SocialPulse — Multi-Platform Social Media Trending Intelligence Dashboard

SocialPulse is an AI-augmented, multi-platform social media intelligence dashboard that aggregates, normalizes, categorizes, and summarizes real-time trending topics across 9 platforms side-by-side.

Designed with rigorous provenance standards, SocialPulse enforces a strict architectural taxonomy separating direct, verified first-party platform data (**Category A**) from derived journalistic reporting and search interest signals (**Category B**). All data is genuine: no fabricated locations, no fake articles, and authentic publication timestamps.

---

## 🏛️ Architecture & Source Classification

To ensure complete transparency, data integrity, and academic honesty, SocialPulse never mocks or scrapes in a way that misrepresents data provenance:

### Category A — Direct Official APIs (3 Platforms)
First-party data ingested directly from platform APIs with authentic engagement metrics (views, posts, interactions):
1. **YouTube** — Official YouTube Data API v3: Dual-list fetch merging `chart=mostPopular` (India, `regionCode=IN`) and `videoCategoryId=25` (News & Politics) with dedicated `[Trending in News]` markers. Recency is anchored to chart snapshot time (`fetched_at`), displaying genuine publication dates separately.
2. **Mastodon** — Official Federated Trends API (`/api/v1/trends/tags`, `/api/v1/trends/statuses`) capturing decentralized Fediverse discourse.
3. **Bluesky** — Official AT Protocol AppView Trends API (`app.bsky.unspecced.getTaggedSuggestions`) tracking viral decentralized network topics.

*Card Styling:* Solid cyan/platform-colored border, **"OFFICIAL API"** badge, filled-dot indicator, and direct platform action link.

---

### Category B — Derived / Journalistic Signals (6 Platforms)
Journalistic media coverage and search interest signals representing cultural and viral trends for platforms without open public trending endpoints:
4. **Google Trends** — Real-time Search Interest via Google Trends Live RSS, enriched with state-level regional interest data via PyTrends for top Indian search trends.
5. **News Coverage: Instagram** — Verified tech & culture journalism covering Instagram viral trends, Reels, and creator discussions.
6. **News Coverage: Facebook** — Verified journalism covering Facebook communities, viral posts, and public debates.
7. **News Coverage: X (Twitter)** — Verified journalism covering trending topics, viral tweets, and community discourse on X.
8. **News Coverage: Reddit** — Verified journalism covering viral Reddit discoveries, thread discussions, and community reactions.
9. **News Coverage: Twitch** — Verified gaming journalism covering record-breaking livestreams, esports tournaments, and streamer developments.

*Card Styling:* Dashed amber border, bold **"SEARCH INTEREST"** or **"NEWS COVERAGE"** badge, diamond indicator, and explicit **"Read Article →"** or **"Explore on Google Trends →"** call to action (never misleading users into thinking it is a direct social post).

---

## 📰 Scaled Journalism & News Coverage Engine

Category B news coverage uses an extensible, config-driven engine (`backend/services/news_sources.py` & `backend/services/news_coverage.py`):
- **30+ Verified Outlets:** Covers leading national Indian news desks (*The Indian Express, News18, India Today, NDTV Profit, The Hindu, Mint, Times of India, Firstpost, Economic Times, Telangana Today, Business Standard, ABP Live, Moneycontrol, Scroll, Deccan Chronicle, MediaNama, Inc42, YourStory, Digit*) and international tech/gaming desks (*TechCrunch, The Verge, Social Media Today, Engadget, Mashable, 9to5Mac, 9to5Google, Ars Technica, Polygon, Esports Insider, GamesRadar*).
- **RSS-First Architecture:** Prefers official RSS/Atom feeds for reliability and courtesy, falling back to HTML section scraping only when feeds are unavailable. Outlets returning 403/404 are logged in `DROPPED_OUTLETS_LOG`.
- **Google News RSS Multi-Query Ingestion:** Runs 4–6 targeted search query variants per platform concurrently, with automated decoding of Google News redirect URLs to original publisher articles via `googlenewsdecoder`.
- **Strict Content Validation:** Ensures every item is genuine third-party journalism (rejecting bare social links, homepages, or unresolved Google redirects) and strictly relevant to platform trending topics.
- **Deduplication & Recency:** Normalized URL deduplication combined with token-based headline overlap detection (>80% similarity). Genuine publication dates and lead images (`og:image`) are extracted from metadata.
- **Concurrency & Courtesy:** Shared concurrency semaphore (8), 6s per-site timeouts, and an in-memory 10-minute cache prevent hammering publisher servers.

---

## 📍 Trending Region Intelligence & Honest Fallback Chain

Every card and the inspection drawer display a resolved trending region with an honest provenance basis (`TrendRegion`: label, scope, basis):
1. **Local Scope (`📍 {City, State}`):** Assigned when specific Indian locations (cities, districts, or states like *Bengaluru, Karnataka*, *Mumbai*, *Warangal, Telangana*, *Karimnagar*) are detected from article text or Gemini analysis. Basis: *"Location detected from the story content"*.
2. **Country Scope (`📍 India`):** Assigned when an article relates to nationwide Indian events, or when ingested from India-filtered queries (Google Trends `geo=IN` or YouTube `regionCode=IN`). Basis: *"Nationwide Indian story"* or *"This source is queried for India (geo/region = IN)"*.
3. **Global Scope (`🌐 Global`):** Assigned when the source or topic has no geographic filter or is international. Basis: *"No regional filter available for this source"*.
4. **Interactive UI:** Region pills feature tooltips showing the exact resolution basis. The slide-over drawer includes a dedicated `.region-box` with cyan accenting detailing the region and basis. A UI dropdown filter allows filtering by *All*, *India-Specific*, or *Global*.

---

## ⚡ Scaled Gemini AI Intelligence

- **Batch Processing:** Processes 8–10 trending items per Gemini prompt, returning structured JSON arrays. This increases processing throughput from ~5 items/min to 40–50 items/min under free-tier limits.
- **Model Fallback Chain:** Automatically fails over across `gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemini-flash-latest`, `gemini-3.7-flash`, and `gemini-3.6-flash` on HTTP 429/503 errors.
- **Single-Item Fallback:** If a batch response omits any item or fails validation, single-item calls are triggered exclusively for the missing items.
- **Strict Accuracy & Hedging:** Preserves unverified claims (*"Reportedly...", "According to unverified social media claims..."*), categorizes creator/streaming content under Gaming or Entertainment, and prohibits generic boilerplate summaries.
- **Honest Failures:** Items that fail AI analysis remain `ai_processed=False` to be retried by the background AI sweep; no fake or mock summaries are ever inserted in live mode.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy ORM, SQLite with Write-Ahead Logging (`WAL` mode with `PRAGMA busy_timeout=5000`), Pydantic v2.
- **AI Engine:** Google Gemini API (`google-generativeai`) with structured JSON schemas and sliding-window rate limiting.
- **Scraping & News:** BeautifulSoup4, lxml, feedparser, googlenewsdecoder, httpx (async).
- **Scheduler:** APScheduler (asyncio) scheduling all enabled sources at DB-configured intervals (Cat A: 15 min, Cat B: 60 min, AI sweep: 5 min) with staggered starts.
- **Frontend:** Vanilla JavaScript SPA (Zero-build, no Node.js required), CSS Custom Properties, interactive canvas particles, responsive drawer inspection.

---

## 🚀 Setup & Installation Guide

### 1. Prerequisites
- **Python 3.11 or higher** installed ([python.org](https://www.python.org/downloads/)).
- **Git** installed ([git-scm.com](https://git-scm.com/)).

---

### 2. Clone the Repository
```bash
git clone https://github.com/thrishi1011/SocialPulse.git
cd SocialPulse
```

---

### 3. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 5. Environment Configuration (`.env`)

Copy `.env.example` to create `.env`:
```powershell
Copy-Item .env.example .env
```

Configure your API keys:
```ini
MOCK_FETCH_MODE=false
MOCK_AI_MODE=false
DB_PATH=socialpulse.db
PIPELINE_INTERVAL_MINUTES=15

# Google Gemini API Key (Required for live AI summaries)
GEMINI_KEY=your_gemini_api_key_here

# YouTube Data API v3 Key (Required for live YouTube trends)
YOUTUBE_API_KEY=your_google_cloud_youtube_key_here
```

---

### 6. Initialize & Seed the Database
```bash
python -m backend.seed
```

---

### 7. Run the Application
```bash
uvicorn backend.main:app --reload --port 8000
```

Open your browser:
- 🌐 **Dashboard UI:** [http://localhost:8000](http://localhost:8000)
- 📚 **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- ❤️ **Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Testing & Verification

Run the complete automated test suite using pytest:
```bash
python -m pytest
```

Or run individual verification test suites:
- `python test_phase1.py` — Database schema, 9-source seeding, mock normalization, and deduplication.
- `python test_phase2.py` — API endpoints, Category A/B provenance separation, recency filtering, and source status.
- `python test_phase3.py` — Frontend delivery, static asset integrity, and SVG icon availability.
- `python test_phase7.py` — Sliding-window rate limiter, live Gemini analysis, and batch DB AI processing.
- `python test_e2e.py` — Complete end-to-end cold-start pipeline verification across all 9 sources.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/trends` | Filter trending items by `source`, `source_category` (A/B), `category`, `recency` (6h/12h/24h), `region_scope` (all/india/global/local), and sort |
| `GET` | `/api/v1/trends/{id}` | Full trend item metadata including raw JSON audit payload and resolved trending region |
| `GET` | `/api/v1/sources` | Status and configuration for all 9 integrated sources |
| `GET` | `/api/v1/sources/{slug}/status` | Ingestion status, error messages, and metrics for a specific source |
| `GET` | `/api/v1/categories` | Complete taxonomy of standard categorization topics with item counts |
| `POST`| `/api/v1/pipeline/run` | Trigger a manual fetch cycle across all active sources (`?force_live=true`) |
| `POST`| `/api/v1/pipeline/run/{slug}` | Trigger a manual fetch cycle for a single source |
| `POST`| `/api/v1/pipeline/process-ai` | Trigger batch Gemini AI summarization on unprocessed items |
| `GET` | `/health` | Application health, database connection status, and enabled sources count |

---

## 📄 License
MIT License. Developed for educational and academic intelligence research.
