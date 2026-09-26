# SocialPulse — Multi-Platform Social Media Trending Intelligence Dashboard

SocialPulse is an AI-augmented, multi-platform social media intelligence dashboard that aggregates, normalizes, categorizes, and summarizes real-time trending topics across 15 platforms side-by-side.

Designed with rigorous provenance standards, SocialPulse enforces a strict architectural taxonomy separating direct, verified first-party platform data (**Category A**) from derived journalistic reporting and search interest signals (**Category B**).

---

## 🏛️ Architecture & Source Classification

To ensure complete transparency, data integrity, and academic honesty, SocialPulse never mocks or scrapes in a way that misrepresents data provenance:

### Category A — Direct Official APIs (9 Platforms)
First-party data ingested directly from platform APIs with authentic engagement metrics (views, stars, upvotes, reactions):
1. **YouTube** — Official YouTube Data API v3 (`videos.list?chart=mostPopular`)
2. **Hacker News** — Official Algolia HN API (`search_by_date?tags=front_page`)
3. **Mastodon** — Official Federated Trends API (`/api/v1/trends/tags`, `/api/v1/trends/statuses`)
4. **Bluesky** — Official AT Protocol AppView Trends API (`app.bsky.unspecced.getTaggedSuggestions`)
5. **Wikipedia** — Official Wikimedia Daily Pageviews API
6. **Dev.to** — Official Public API (`/api/articles?top=1`)
7. **Lemmy** — Official Federated API (`https://lemmy.world/api/v3/post/list?sort=Hot`)
8. **GitHub Trending** — Official GitHub REST Search API (`/search/repositories`)
9. **Giphy** — Official Giphy Trending API (`/v1/gifs/trending`)

*Card Styling:* Solid cyan/platform-colored border, **"OFFICIAL API"** badge, filled-dot indicator, and direct platform action link.

---

### Category B — Derived / Journalistic Signals (6 Platforms)
Journalistic media coverage and search interest signals representing cultural and viral trends for platforms without open public trending endpoints:
10. **Google Trends** — Real-time Search Interest via Google Trends Live RSS Feed
11. **News Coverage: Instagram** — Verified tech & culture journalism covering Instagram viral trends
12. **News Coverage: Facebook** — Verified journalism covering Facebook communities and viral posts
13. **News Coverage: X (Twitter)** — Verified journalism covering trending topics and viral discourse on X
14. **News Coverage: Reddit** — Verified journalism covering viral Reddit discoveries and discussions
15. **News Coverage: Twitch** — Verified gaming journalism covering record-breaking livestreams and creators

*Card Styling:* Dashed amber border, bold **"SEARCH INTEREST"** or **"NEWS COVERAGE"** badge, diamond indicator, and explicit **"Read Article →"** or **"Explore on Google Trends →"** call to action (never misleading users into thinking it is a direct social post).

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy ORM, SQLite with Write-Ahead Logging (`WAL` mode with `PRAGMA busy_timeout=5000`), Pydantic v2.
- **AI Intelligence:** Google Gemini AI models (`gemini-flash-latest`, `gemini-3.5-flash-lite`, `gemini-3.7-flash`) with structured JSON schema outputs, automated model fallback, and sliding-window rate limiting.
- **Background Scheduler:** APScheduler (asyncio) with staggered execution intervals per source.
- **Frontend:** Vanilla JavaScript SPA (Zero-build, no Node.js required), CSS Custom Properties, Canvas Particle Network, accessible WCAG contrast compliance.

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
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
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

Copy the provided `.env.example` file to create your local `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

Open `.env` in any text editor and configure your settings:
```ini
# App Execution Mode
MOCK_FETCH_MODE=false
MOCK_AI_MODE=false

# Database Configuration
DB_PATH=socialpulse.db
PIPELINE_INTERVAL_MINUTES=15

# Google Gemini API Key (Required for live AI summaries)
# Get a free key at https://aistudio.google.com/
GEMINI_KEY=your_gemini_api_key_here

# Optional Direct Platform API Keys
YOUTUBE_API_KEY=your_google_cloud_youtube_key_here
GIPHY_API_KEY=your_giphy_api_key_here
```

> **Note on Security:** The `.env` file is strictly ignored in `.gitignore` and will never be tracked or pushed to GitHub. Never commit your private API keys.

---

### 6. Initialize & Seed the Database
Run the seed script to create the SQLite schema and populate default sources and categories:
```bash
python -m backend.seed
```

---

### 7. Run the Application
Start the FastAPI server using Uvicorn:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Once started, open your web browser:
- 🌐 **Dashboard UI:** [http://localhost:8000](http://localhost:8000) (or `http://127.0.0.1:8000`)
- 📚 **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- ❤️ **Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Testing & Verification

Run the end-to-end automated verification pipeline:
```bash
python test_e2e.py
```
This script executes a cold-start initialization, tests all 15 source ingestion pipelines, verifies Gemini AI batch processing, and validates all REST endpoints.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/trends` | Filter trending items by source, category, recency (6h/12h/24h), and sort |
| `GET` | `/api/v1/trends/{id}` | Full trend item metadata including raw JSON audit payload |
| `GET` | `/api/v1/sources` | Status and configuration for all 15 integrated sources |
| `GET` | `/api/v1/categories` | Complete taxonomy of standard categorization topics |
| `POST`| `/api/v1/pipeline/run` | Trigger a manual fetch cycle across all active sources |
| `POST`| `/api/v1/pipeline/process-ai` | Trigger batch Gemini AI summarization on unprocessed items |
| `GET` | `/health` | Application health and database connection status |

---

## 👨‍🏫 Demonstration Features & Evaluation Guide

1. **Category A vs Category B Separation:**
   - Use the segmented control at the top of the dashboard (`All Sources (15)`, `Official APIs (Cat A)`, `Derived Signals (Cat B)`).
   - Category A shows cyan solid borders and "Official API" badges; Category B shows amber dashed borders and "NEWS COVERAGE" / "SEARCH INTEREST" badges.
2. **Provenance & Link Integrity:**
   - Category A cards link directly to authentic platform posts (e.g. GitHub repos, Hacker News discussions, Dev.to articles).
   - Category B cards link directly to published third-party journalism (e.g. TechCrunch, Wired, The Guardian), avoiding misleading direct social links.
3. **AI Intelligence & Summary Hedging:**
   - Review the `✨ Why It's Trending` section on each card, generated by Gemini Flash.
   - For unverified social media claims (e.g., anonymous Reddit posts), the AI summary rigorously preserves hedging language (*"Reportedly...", "According to unverified claims..."*) rather than flattening rumors into established facts.
4. **Target Location Badges:**
   - Geographic context is displayed with `📍 Location` chips on both the grid card and inside the slide-over detail drawer for items with identifiable geographic ties (e.g., `📍 Bengaluru, Karnataka`, `📍 Mumbai, Maharashtra`).
5. **Data Auditability:**
   - Click any card to open the slide-over inspection drawer and inspect the stored `raw_json` response payload directly from the platform.
6. **Graceful Fallback Mode:**
   - Set `MOCK_FETCH_MODE=true` in `.env` to run the dashboard completely offline without network dependencies.

---

## 📄 License
MIT License. Developed for educational and academic intelligence research.
