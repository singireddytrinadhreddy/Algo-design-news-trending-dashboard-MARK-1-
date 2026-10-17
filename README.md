# SocialPulse

**SocialPulse** is a multi-source trending-intelligence dashboard that brings social-platform trends, search-interest signals, and journalism about online trends into one interface. It uses a Python API and a lightweight browser frontend, with optional Gemini-powered summaries and categorization.

The goal is to help users explore what is gaining attention, where a story appears to be relevant, and what credible reporting says about it—while making it clear whether an item comes from a platform API, search data, or third-party news coverage.

## 🚀 Features

- **Multi-platform dashboard:** Explore trends from nine sources in one place.
- **AI-powered analysis:** Use Google Gemini to summarize and categorize trending topics.
- **Regional intelligence:** Browse trends associated with local Indian locations, India-wide events, and global topics.
- **Live data ingestion:** Fetch trend data from supported platform APIs, search feeds, and news sources.
- **News coverage engine:** Collect and filter published journalism about trends involving Instagram, Facebook, X, Reddit, and Twitch.
- **Automated refreshes:** Schedule recurring data-fetching and AI-processing jobs.
- **Filtering and sorting:** Explore items by source, category, recency, region, and engagement.
- **Persistent storage:** Store trends, categories, source configurations, and fetch logs in SQLite.
- **Interactive API documentation:** Explore endpoints through FastAPI's Swagger UI.
- **Mock development mode:** Run the dashboard with local fixture data without requiring API keys.

## 🌐 Data Sources

SocialPulse separates direct platform data from derived search-interest and news signals to make data provenance transparent.

### Category A — Direct Platform APIs

These sources retrieve data directly from their respective platform endpoints.

| Platform | Data collected | API key required |
|---|---|---|
| YouTube | Popular videos in India and News & Politics videos | Yes |
| Mastodon | Trending hashtags and related metrics | No |
| Bluesky | Trending topics | No |

### Category B — Search Interest and News Coverage

These sources provide search trends or published journalism about social-media activity. They are not presented as direct social posts.

| Source | Data collected |
|---|---|
| Google Trends | Trending search queries from India |
| Instagram News | News coverage about Instagram trends, Reels, and creators |
| Facebook News | News coverage about Facebook trends and discussions |
| X (Twitter) News | News coverage about trending topics and viral discussions on X |
| Reddit News | News coverage about Reddit threads and community discussions |
| Twitch News | News coverage about streamers, gaming, and livestreaming trends |

The news engine uses configured publisher RSS feeds, publisher pages, and Google News RSS results. It validates article links, extracts available publication metadata, and removes duplicate or near-duplicate headlines.

**Important:** Category B results represent journalism and search-interest signals, not verified platform-wide trending rankings. Source availability, network access, rate limits, and changes to external websites can affect results.

## 🧠 How It Works

1. **Data collection:** Fetchers retrieve data from platform APIs, search feeds, and news sources.
2. **Normalization:** Source-specific data is converted into a common trend-item format.
3. **Validation and deduplication:** Duplicate records are identified and fetch outcomes are recorded.
4. **Database storage:** Items, categories, sources, and fetch logs are stored in SQLite.
5. **AI processing:** Gemini can generate summaries, categorize items, and help identify relevant locations.
6. **Dashboard rendering:** The frontend retrieves API data and displays trends with filters and details.
7. **Scheduled updates:** APScheduler periodically refreshes sources and processes items awaiting AI analysis.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.11+ |
| Backend API | FastAPI |
| ASGI server | Uvicorn |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data validation | Pydantic |
| AI processing | Google Gemini API |
| HTTP requests | HTTPX |
| RSS feed processing | feedparser |
| HTML parsing | BeautifulSoup4, lxml |
| News URL decoding | googlenewsdecoder |
| Scheduling | APScheduler |
| Frontend | HTML, CSS, vanilla JavaScript |
| Testing | pytest, pytest-asyncio |
| Deployment configuration | Render |

The frontend does not require Node.js or a separate build step.

## 📂 Project Structure

```text
SocialPulse/
├── backend/
│   ├── fetchers/
│   │   ├── base.py
│   │   ├── youtube_fetcher.py
│   │   ├── mastodon_fetcher.py
│   │   ├── bluesky_fetcher.py
│   │   ├── google_trends_fetcher.py
│   │   ├── instagram_news_fetcher.py
│   │   ├── facebook_news_fetcher.py
│   │   ├── twitter_news_fetcher.py
│   │   ├── reddit_news_fetcher.py
│   │   └── twitch_news_fetcher.py
│   ├── mock/
│   │   └── Local JSON fixture data
│   ├── routers/
│   │   ├── trends.py
│   │   ├── sources.py
│   │   ├── categories.py
│   │   └── pipeline.py
│   ├── services/
│   │   ├── orchestrator.py
│   │   ├── ai_processor.py
│   │   ├── mock_ai.py
│   │   ├── news_coverage.py
│   │   ├── news_sources.py
│   │   └── scheduler.py
│   ├── utils/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
├── frontend/
│   ├── assets/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   └── utils.js
│   └── index.html
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── test_phase1.py
├── test_phase2.py
├── test_phase3.py
├── test_phase7.py
└── test_e2e.py
```

## 💻 Installation and Setup

### 1. Prerequisites

Install the following:

- Python 3.11 or later
- Git

Python downloads: https://www.python.org/downloads/

Git downloads: https://git-scm.com/downloads

Verify the installations:

```bash
python --version
git --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/thrishi1011/SocialPulse.git
cd SocialPulse
```

### 3. Create a Virtual Environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

A virtual environment keeps the project's Python dependencies separate from other Python projects.

### 4. Install Dependencies

With the virtual environment activated, run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory.

**Windows — PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Open `.env` in your editor and choose one of the following configurations.

#### Option A: Run in Mock Mode

Mock mode is the easiest way to explore the application without configuring API credentials.

Set the following values:

```dotenv
MOCK_FETCH_MODE=true
MOCK_AI_MODE=true
LIVE_SOURCES=
DB_PATH=socialpulse.db
PIPELINE_INTERVAL_MINUTES=15
```

**Important:** Set `LIVE_SOURCES` explicitly to an empty value. The application's default configuration otherwise lists the nine configured sources as live sources, which can cause live fetches even when `MOCK_FETCH_MODE=true`.

Mock mode uses local JSON fixtures and mock/heuristic AI processing. It is intended for development and demonstration, not for displaying current trends.

#### Option B: Run with Live Data and Gemini AI

For live source fetching and Gemini-powered analysis, configure:

```dotenv
MOCK_FETCH_MODE=false
MOCK_AI_MODE=false
DB_PATH=socialpulse.db
PIPELINE_INTERVAL_MINUTES=15

YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_KEY=your_gemini_api_key
```

**YouTube API key**

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable **YouTube Data API v3**.
4. Open the credentials section and create an API key.
5. Add the key to `YOUTUBE_API_KEY` in `.env`.

**Gemini API key**

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Create an API key.
3. Add the key to `GEMINI_KEY` in `.env`.

Mastodon, Bluesky, Google Trends RSS, and the configured news-coverage sources do not require API keys for the standard nine-source pipeline, but they need network access and functioning external endpoints.

The project also defines optional settings for integrations such as NewsAPI, GNews, GIPHY, Reddit, Twitch, and Pinterest. These are not required for the standard nine-source dashboard.

**Security:** Never commit your `.env` file or publish API keys. The repository's `.gitignore` excludes `.env`.

### 6. Initialize the Database

The application initializes and seeds the SQLite database automatically during startup, so this step is normally optional.

To initialize and seed it manually, run:

```bash
python -m backend.seed
```

By default, the database is stored as `socialpulse.db` in the project root.

### 7. Start the Application

From the repository root, run:

```bash
uvicorn backend.main:app --reload --port 8000
```

Wait for the server to complete its startup process, then open the dashboard in your browser.

| Service | URL |
|---|---|
| SocialPulse Dashboard | http://127.0.0.1:8000 |
| Swagger API Documentation | http://127.0.0.1:8000/docs |
| ReDoc API Documentation | http://127.0.0.1:8000/redoc |
| Health Check | http://127.0.0.1:8000/health |

To stop the development server, press `Ctrl+C` in the terminal.

## 📡 API Endpoints

The backend exposes a versioned API under `/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks application and database health |
| GET | `/api/v1/trends` | Retrieves and filters trending items |
| GET | `/api/v1/trends/{item_id}` | Retrieves details about a specific trend item |
| GET | `/api/v1/sources` | Lists configured data sources |
| GET | `/api/v1/sources/{slug}/status` | Retrieves the fetch status of a source |
| GET | `/api/v1/categories` | Lists categories and item counts |
| GET | `/api/v1/pipeline/status` | Displays pipeline activity and AI-processing metrics |
| POST | `/api/v1/pipeline/run` | Triggers ingestion across enabled sources |
| POST | `/api/v1/pipeline/run/{slug}` | Triggers ingestion for a particular source |
| POST | `/api/v1/pipeline/process-ai` | Processes pending items using Gemini or mock AI |

The trends endpoint supports filtering by parameters such as source, source category, category, recency, and region scope. It also supports sorting and pagination.

### Example API Requests

Check application health:

```bash
curl http://127.0.0.1:8000/health
```

List all sources:

```bash
curl http://127.0.0.1:8000/api/v1/sources
```

Retrieve recent trends:

```bash
curl "http://127.0.0.1:8000/api/v1/trends?recency=24h"
```

Check pipeline status:

```bash
curl http://127.0.0.1:8000/api/v1/pipeline/status
```

Trigger a source-fetching cycle:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/pipeline/run"
```

Force a fetch cycle to use live fetchers:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/pipeline/run?force_live=true"
```

Live fetching can fail or fall back to fixture data when a provider is unavailable or required credentials are missing. Check the response and server logs to confirm the outcome of a fetch.

For all supported query parameters and response schemas, visit:

http://127.0.0.1:8000/docs

## 🧪 Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest -q
```

The repository includes the following test modules:

| Test file | Purpose |
|---|---|
| `test_phase1.py` | Database initialization, source/category seeding, and fetching pipeline checks |
| `test_phase2.py` | API behavior and source/provenance checks |
| `test_phase3.py` | Frontend delivery and static-resource checks |
| `test_phase7.py` | Rate limiting and AI-processing checks |
| `test_e2e.py` | End-to-end cold-start pipeline verification |

Run an individual test module using:

```bash
python -m pytest test_phase1.py
```

Tests involving live services may depend on network access, third-party availability, and API quotas. Use mock mode when you need predictable local data.

## 🚢 Deployment

The repository contains a `render.yaml` file for configuring deployment on Render.

General deployment steps:

1. Push the repository to GitHub.
2. Create a new web service on Render and connect the repository.
3. Review the build and start commands in `render.yaml`.
4. Configure required environment variables through the hosting provider's dashboard.
5. Deploy and verify the service using `/health` and the dashboard URL.

The deployment configuration uses Python 3.11 and starts the app with Uvicorn.

Keep credentials such as `GEMINI_KEY` and `YOUTUBE_API_KEY` in the deployment environment settings, not in committed source files.

Before using the application in a public production environment, review CORS settings, API access, request limits, monitoring, and logging.

## 🔧 Troubleshooting

### The dashboard opens but no items appear

Check:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/v1/sources
- http://127.0.0.1:8000/api/v1/pipeline/status

Also review the terminal output for fetch errors.

### YouTube data does not load

Verify that:

- `YOUTUBE_API_KEY` is set correctly.
- YouTube Data API v3 is enabled in Google Cloud.
- The API key and project have available quota.

### Gemini summaries are missing

Check that `GEMINI_KEY` is configured and `MOCK_AI_MODE=false`. API quotas, unavailable models, or network issues can prevent live analysis.

### Mock mode unexpectedly makes live requests

Set all three values in `.env`:

```dotenv
MOCK_FETCH_MODE=true
MOCK_AI_MODE=true
LIVE_SOURCES=
```

Restart the server after changing environment variables.

### A source is unavailable

Inspect the source's status endpoint:

```text
http://127.0.0.1:8000/api/v1/sources/youtube/status
```

Replace `youtube` with the appropriate source slug. External APIs, RSS feeds, and publisher websites can change or become temporarily unavailable.

## 🔐 Data and Privacy Notes

- API keys should be stored in environment variables.
- Live data and local fixture data should not be treated as interchangeable.
- Search interest and journalism do not necessarily reflect official platform-wide rankings.
- Regional labels are based on available source information and analysis, not guaranteed geographic tracking.
- External publishers retain control over their content and availability.

## 📄 License

No `LICENSE` file is currently included in this repository. Add an appropriate license file before specifying reuse or redistribution terms.
