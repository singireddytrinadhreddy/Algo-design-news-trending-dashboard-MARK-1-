# SocialPulse — Multi-Platform Social Media Trending Intelligence Dashboard

SocialPulse is an AI-augmented, multi-platform social media intelligence dashboard that aggregates, normalizes, categorizes, tracks, and analyzes real-time trending topics across 9 platforms side-by-side.

Designed with rigorous provenance standards, SocialPulse enforces a strict architectural taxonomy separating direct, verified first-party platform data (**Category A**) from derived journalistic reporting and search interest signals (**Category B**). All data is genuine: no fabricated locations, no fake articles, honest metric representation, and authentic publication timestamps.

---

## 📑 Table of Contents
1. [Architecture & Source Classification](#-architecture--source-classification)
2. [Macro Stories & Cross-Platform Topic Clustering](#-macro-stories--cross-platform-topic-clustering)
3. [Trend Velocity & Momentum Engine](#-trend-velocity--momentum-engine)
4. [Analytics Dashboard](#-analytics-dashboard)
5. [Source Health Observatory](#-source-health-observatory)
6. [Client Watchlist, Bookmarks & Secure CSV Export](#-client-watchlist-bookmarks--secure-csv-export)
7. [Trending Region Intelligence & Honest Fallback Chain](#-trending-region-intelligence--honest-fallback-chain)
8. [Algorithms & Plain-English Viva Defense Guide](#-algorithms--plain-english-viva-defense-guide)
9. [Database Persistence & Dynamic Migrations](#-database-persistence--dynamic-migrations)
10. [Honest Academic Limitations](#-honest-academic-limitations)
11. [Setup & Installation Guide](#-setup--installation-guide)
12. [Automated Verification & Test Suite](#-automated-verification--test-suite)
13. [Complete API Endpoints Reference](#-complete-api-endpoints-reference)

---

## 🏛️ Architecture & Source Classification

To ensure complete transparency, data integrity, and academic honesty, SocialPulse never scrapes in a way that misrepresents data provenance:

### Category A — Direct Official APIs (3 Platforms)
First-party data ingested directly from official platform APIs with authentic engagement metrics (views, posts, interactions):
1. **YouTube** — Official YouTube Data API v3: Dual-list fetch merging `chart=mostPopular` (India, `regionCode=IN`) and `videoCategoryId=25` (News & Politics) with dedicated `[Trending in News]` markers. Recency is anchored to chart snapshot time (`fetched_at`), displaying genuine video publication dates separately.
2. **Mastodon** — Official Federated Trends API (`/api/v1/trends/tags`, `/api/v1/trends/statuses`) capturing decentralized Fediverse discourse.
3. **Bluesky** — Official AT Protocol AppView Trends API (`app.bsky.unspecced.getTaggedSuggestions`) tracking viral decentralized network topics.

*Card Styling:* Solid cyan border, bold **"OFFICIAL API"** badge, filled-dot indicator, and direct platform action link.

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

## 🌐 Macro Stories & Cross-Platform Topic Clustering

When a major event occurs (such as an ISRO space mission or a major sports final), it trends across multiple social media platforms simultaneously. SocialPulse identifies these cross-platform phenomena as **Macro Stories**.

- **Convergence Definition:** A story is designated as **cross-platform converged** only when $\ge 2$ distinct sources report on the exact same real-world event.
- **Two-Tier Engine:** Combines an offline Jaccard token similarity with Disjoint Set Union (DSU) clustering and a batched Gemini LLM refinement pass.
- **Incremental Association:** New incoming trends are checked against active topics first to track narrative evolution over time, preventing duplicate topics. Topics idle for $> 48$ hours are automatically marked inactive.
- **Batched Editorial Summaries:** The AI synthesizes concise 2–3 sentence cross-platform summaries (`batch size <= 5`) contrasting how different platforms are covering the story.
- **UI Experience:** Dedicated **Stories** view (`#/topics`) with platform coverage pills, cross-source count indicators, expandable item trays, and clickable topic badges on individual feed cards.

---

## 📈 Trend Velocity & Momentum Engine

SocialPulse tracks the temporal trajectory of trends using a dedicated time-series snapshot mechanism (`trend_snapshots`):

- **Automated Snapshots:** On every fetch cycle, items with rank or engagement metrics record a snapshot (`rank`, `engagement_value`, `secondary_value`, `captured_at`). A 5-minute deduplication window prevents redundant entries, and a background maintenance task prunes snapshots older than 7 days.
- **Velocity State Machine:** Categorizes momentum into 6 explainable states:
  - `🔥 Surging`: Rapidly climbing rank ($\ge 3$ spots) or high hourly engagement growth ($> 15\%$/hr).
  - `📉 Cooling`: Falling rank ($\ge 3$ spots) or negative growth ($< -10\%$/hr).
  - `⭐ Peaking`: Reached a high apex in recent cycles and growth is leveling off.
  - `➡️ Steady`: Consistent engagement and position over multiple hours.
  - `✨ New`: Single snapshot detected within the last hour.
  - `⏳ Tracking`: Insufficient snapshot history (e.g. $< 10$ minutes). Displays an honest *"Collecting data…"* indicator.
- **Inline SVG Sparklines:** Interactive, lightweight SVG mini-charts embedded directly inside feed cards showing the trajectory over the last 12–24 hours.
- **Inspection Drawer Analytics:** Full Chart.js line chart in the slide-over detail drawer plotting exact snapshot points over time.
- **Sorting:** Dedicated `sort=momentum` option ranking fastest-accelerating trends first.

---

## 📊 Analytics Dashboard

An integrated analytical view (`#/analytics`) powered by SQL aggregate queries (`GROUP BY`) delivering zero-latency data intelligence:

- **Category Breakdown:** Donut chart of item distribution across 12 standard taxonomy categories.
- **Platform Share:** Horizontal bar chart comparing item volume per source (strictly using item counts; never comparing incomparable metrics like views vs upvotes).
- **Category A vs Category B Ratio:** Provenance balance donut highlighting the proportion of first-party API data versus journalistic coverage.
- **Top Indian Locations:** Bar chart of geographic concentrations identified within story contents (Bengaluru, Warangal, Delhi, Mumbai, etc.).
- **24-Hour Volume Timeline:** Line chart showing total items ingested per hour with zero-filled empty buckets for time-series integrity.
- **AI Processing Coverage:** Live KPI stat tile showing processed, pending, and percentage coverage.
- **Recency Filtering:** Global toggle for `6h`, `12h`, `24h`, and `All Time` recalculations.

---

## 🩺 Source Health Observatory

A transparency and operational monitoring dashboard (`#/health`) providing visibility into data freshness and pipeline status:

- **Derived Status States:**
  - `🟢 Healthy`: Successful fetch within expected interval $\times 2$.
  - `🟡 Stale`: No successful fetch for $> 2 \times \text{interval}$.
  - `🟠 Degraded`: Running on fallback data or error rate $> 30\%$.
  - `🔴 Error`: Last fetch attempt failed with an explicit error.
  - `⚪ Disabled`: Source administratively disabled in settings.
  - `⚫ Never Run`: No fetch logs recorded yet.
- **Health Indicators:** Relative timestamps ("2m ago"), 24-hour success rate progress bars, and execution duration metrics.
- **Log Drawer:** Clickable rows open expandable audit drawers displaying the last 20 execution attempts with timestamps, durations, item counts, and raw error messages.
- **Manual Trigger:** On-demand "Run Now" button allowing immediate single-source pipeline testing.
- **Auto-Refresh:** Passive 30-second polling keeping observatory status current without manual page reloads.

---

## 🔍 Client Watchlist, Bookmarks & Secure CSV Export

- **Keyword Watchlist:** Instant client-side tracking using browser `localStorage`. Enter keywords (e.g. "ISRO", "AI", "Cricket", "Election") to filter the feed and highlight matching trends with cyan badges.
- **Bookmarks (Saved Items):** Star favorite trends to keep them in a dedicated local collection accessible via the "Saved" filter toggle.
- **Secure CSV Export (`GET /api/v1/trends/export.csv`):** Export filtered datasets directly into spreadsheet-ready format.
  - **CWE-1236 Anti-Formula Injection Guard:** To eliminate CSV Formula Injection vulnerabilities in Excel and Google Sheets, any field starting with `=`, `+`, `-`, or `@` is automatically sanitized by prefixing a single quote (`'`).

---

## 📍 Trending Region Intelligence & Honest Fallback Chain

Every card and inspection drawer displays a resolved trending region with an honest provenance basis (`TrendRegion`: label, scope, basis):
1. **Local Scope (`📍 {City, State}`):** Assigned when specific Indian locations (cities, districts, or states like *Bengaluru, Karnataka*, *Warangal, Telangana*, *Mumbai*) are detected from article text or Gemini analysis. Basis: *"Location detected from the story content"*.
2. **Country Scope (`📍 India`):** Assigned when an article relates to nationwide Indian events, or when ingested from India-filtered queries (Google Trends `geo=IN` or YouTube `regionCode=IN`). Basis: *"Nationwide Indian story"* or *"This source is queried for India (geo/region = IN)"*.
3. **Global Scope (`🌐 Global`):** Assigned when the source or topic has no geographic filter or is international. Basis: *"No regional filter available for this source"*.
4. **Interactive UI:** Region pills feature tooltips showing the exact resolution basis. The slide-over drawer includes a dedicated `.region-box` with cyan accenting detailing the region and basis.

---

## 🧠 Algorithms & Plain-English Viva Defense Guide

Use this section to confidently explain every algorithm during project defense, evaluation, or viva voce:

### 1. Trend Momentum & Velocity Math
**Question:** *How do you measure if a trend is rising or dying without fake data?*

**Answer:**
We track changes between periodic snapshots stored in the `trend_snapshots` table:
$$\Delta rank = rank_{\text{old}} - rank_{\text{latest}}$$
*(A positive $\Delta rank$ indicates climbing closer to #1).*

Normalized hourly growth rate:
$$\text{Growth Rate } G = \frac{V_{\text{latest}} - V_{\text{old}}}{\Delta t_{\text{hours}} \times \max(V_{\text{old}}, 1)}$$

**State Rules:**
- If only 1 snapshot exists and $\le 1$h old $\rightarrow$ `new`.
- If observation span $\Delta t < 10$ minutes $\rightarrow$ `tracking` (*"Collecting data…"*).
- If $\Delta rank \ge 3$ OR $G > 0.15$ ($> 15\%$/hr) $\rightarrow$ `surging`.
- If $\Delta rank \le -3$ OR $G < -0.10$ ($< -10\%$/hr) $\rightarrow$ `cooling`.
- If highest value occurred mid-window and growth is now flat $\rightarrow$ `peaking`.
- If snapshots span $> 30$ mins with growth between $-5\%$ and $+10\%$ $\rightarrow$ `steady`.

---

### 2. Topic Clustering Pipeline (Two-Tier Architecture)
**Question:** *How do you group trends across platforms without blowing through LLM rate limits?*

**Answer:**
We use a two-tiered clustering architecture:
1. **Pre-Pass Normalization:** Titles are lowercased, punctuation is stripped, and a set of 50+ common English stopwords (`the`, `with`, `breaking`, `about`, etc.) are removed.
2. **Deterministic Jaccard Fallback:**
   $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
   Pairs with $J(A, B) \ge 0.5$ are merged using a Disjoint Set Union (DSU / Union-Find) data structure. This guarantees complete clustering even if Gemini is completely offline.
3. **Batched Gemini Refinement:**
   If Gemini is active, compact payloads of up to 60 items per batch (max 2 calls per run) are evaluated by the LLM. The prompt strictly instructs grouping only identical real-world events.
4. **Validation Guard:** The backend strictly verifies that every ID returned by the LLM exists in the batch, discards single-item groups, and ensures no duplicate memberships.
5. **Cross-Platform Condition:** A topic is marked as cross-platform if and only if:
   $$\text{Distinct Sources Count} \ge 2$$

---

### 3. CSV Formula Injection Defense
**Question:** *Why is sanitizing CSV exports important?*

**Answer:**
When Excel or LibreOffice opens a CSV file, cells beginning with `=`, `+`, `-`, or `@` are interpreted as formulas (CWE-1236). Attackers can inject commands like `=cmd|' /C calc'!A0`. SocialPulse enforces RFC 4180 escaping and prefixes any formula character with a single quote (`'`), rendering it as harmless static text.

---

## 🗄️ Database Persistence & Dynamic Migrations

SocialPulse supports both **SQLite** for zero-setup local development and **PostgreSQL** for persistent cloud deployment (e.g. Render, Supabase, Neon):

- **Environment-Driven Configuration:** `DATABASE_URL` is parsed in `backend/config.py`. URLs beginning with `postgres://` are automatically normalized to `postgresql://` for `psycopg2` compatibility. If empty, local SQLite (`sqlite:///socialpulse.db`) is used.
- **Dialect Isolation:**
  - SQLite: Applies `connect_args={"check_same_thread": False}` and the SQLite WAL PRAGMA listener.
  - PostgreSQL: Applies connection pool configuration `pool_pre_ping=True`, `pool_size=5`, and `max_overflow=5`.
- **Dynamic Startup Migrations (`backend/migrations.py`):**
  SQLAlchemy's `Base.metadata.create_all()` creates missing tables but does not add newly defined columns to existing tables. SocialPulse inspects table schemas dynamically using `sqlalchemy.inspect(engine)` and runs idempotent `ALTER TABLE ... ADD COLUMN` statements (e.g. adding `topic_id` to `trending_items`) on both SQLite and PostgreSQL.

---

## ⚖️ Honest Academic Limitations

In accordance with our academic transparency guidelines:
1. **Snapshot Cadence:** Trend velocity and sparklines require at least two distinct fetch cycles ($\ge 10$ minutes apart) to calculate delta metrics. Items with only one snapshot display an honest `"Collecting data…"` badge rather than fabricated curves.
2. **Probabilistic Topic Correlation:** Macro Story clustering relies on token overlap and language model inference. Subtly distinct developments in the same overall news cycle may occasionally be merged or split.
3. **Regional Localization Scope:** The `location_india` field reflects the geographical setting of the reported event (e.g., an incident in Bengaluru), not the physical location of the social media users reading or discussing the post.

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

Configure your environment variables:
```ini
# App Mode
MOCK_FETCH_MODE=false
MOCK_AI_MODE=false

# Database Configuration (Leave empty for local SQLite)
DATABASE_URL=
DB_PATH=socialpulse.db

# Pipeline Scheduler Interval
PIPELINE_INTERVAL_MINUTES=15

# Google Gemini API Key (Required for live AI summaries & macro stories)
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

## 🧪 Automated Verification & Test Suite

Run the automated test suite verifying all 5 phases:
```bash
python -m pytest test_phase1.py test_phase2.py test_phase3.py test_e2e.py test_phase8.py -v
```

### Test Suite Structure:
- `test_phase8.py` (13 tests) — Verifies:
  - Velocity state machine transitions (`surging`, `cooling`, `peaking`, `steady`, `new`, `tracking`).
  - Topic clustering heuristics, LLM ID validation, and cross-platform convergence ($\ge 2$ sources).
  - Analytics aggregate calculations and 24-hour zero-filled volume buckets.
  - Source health state derivations (`healthy`, `stale`, `degraded`, `error`, `disabled`, `never_run`).
  - CSV export sanitization and anti-formula injection guards.
- `test_phase1.py` (4 tests) — Database schema, 9-source seeding, mock normalization, and deduplication.
- `test_phase2.py` (1 test) — REST API endpoints, Category A/B provenance separation, recency filtering.
- `test_phase3.py` (1 test) — Zero-build frontend delivery, static asset integrity, SVG icons.
- `test_e2e.py` (1 test) — End-to-end cold-start pipeline verification across all 9 sources.

---

## 📡 Complete API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/trends` | Filter trending items by `source`, `source_category` (A/B), `category`, `recency` (6h/12h/24h), `region_scope`, and `sort` (rank/recency/engagement/momentum) |
| `GET` | `/api/v1/trends/{id}` | Full trend item metadata including raw JSON payload, trending region, and momentum details |
| `GET` | `/api/v1/trends/{id}/history` | Historical snapshot points for charting trend rank and engagement trajectory |
| `GET` | `/api/v1/trends/export.csv` | Download CSV export of currently filtered trends with anti-injection sanitization |
| `GET` | `/api/v1/topics` | List active macro stories (`?min_sources=2&recency=24h`) with cross-platform convergence status |
| `GET` | `/api/v1/topics/{id}` | Detailed topic metadata, cross-platform editorial summary, and member trending items |
| `GET` | `/api/v1/analytics/overview` | SQL aggregated analytics metrics (`category_breakdown`, `platform_share`, `hourly_volume`, etc.) |
| `GET` | `/api/v1/sources` | Metadata, icons, and configuration for all 9 integrated sources |
| `GET` | `/api/v1/sources/health` | Real-time source health observatory with derived states, 24h success rates, and last fetch details |
| `GET` | `/api/v1/sources/{slug}/logs` | Ingestion execution logs for audit trail inspection |
| `GET` | `/api/v1/sources/{slug}/status` | Status, error messages, and metrics for a single source |
| `GET` | `/api/v1/categories` | Complete taxonomy of standard categorization topics with item counts |
| `POST`| `/api/v1/pipeline/run` | Trigger a manual fetch cycle across all active sources (`?force_live=true`) |
| `POST`| `/api/v1/pipeline/run/{slug}` | Trigger a manual fetch cycle for a single source |
| `POST`| `/api/v1/pipeline/process-ai` | Trigger batch Gemini AI summarization on unprocessed items |
| `GET` | `/health` | Core system health, database connection status, and active sources count |

---

## 📄 License
MIT License. Developed for educational, research, and social intelligence demonstration.
