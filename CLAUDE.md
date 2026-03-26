# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A retail product recommendation API built with FastAPI, PostgreSQL, and Redis. It supports multiple recommendation strategies (collaborative filtering, trending, content-based) with Redis caching and A/B testing support.

## Stack

- **API**: FastAPI + Uvicorn
- **DB**: PostgreSQL 15 (via psycopg2)
- **Cache**: Redis 7
- **ML**: scikit-learn, pandas, numpy
- **Validation**: Pydantic v2
- **Tests**: pytest + httpx (async test client)

## Setup

Copy `.env.example` to `.env` and adjust values as needed.

Start dependencies:
```bash
docker-compose up -d
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Seed the database:
```bash
python -m data.seed_db
```

Run the API:
```bash
uvicorn backend.main:app --reload --port 8000
```

## Tests

```bash
pytest                        # run all tests
pytest tests/test_api.py      # run a single test file
pytest -k "test_name"         # run a single test by name
```

## Architecture

```
backend/
  config.py       # loads .env via python-dotenv; single Settings object used throughout
  schemas.py      # Pydantic v2 models for API request/response shapes
  cache.py        # Redis client wrapper; TTL driven by REDIS_TTL_SECONDS env var
  recommender.py  # recommendation strategies (collaborative, trending, content-based)
  main.py         # FastAPI app, route definitions, dependency injection
  ab_testing.py   # A/B agent: deterministic session-hash variant assignment
  stats.py        # statistical engine (z-test, Wilson CI, Cohen's h, Bayesian MC)
  analytics.py    # PostgreSQL event storage and metrics aggregation queries
  dashboard.py    # self-contained HTML dashboard served at GET /dashboard

data/
  products.py     # product data models / DB access layer
  seed_db.py      # one-time script to populate PostgreSQL with sample data

frontend/
  public/
    analytics.js  # browser event tracker — sends events to POST /events with variant

tests/
  test_strategies.py  # unit tests for recommender logic
  test_api.py         # integration tests against the FastAPI app via httpx
```

**Request flow**: FastAPI route → check Redis cache → if miss, run recommender strategy → write result to cache → return response.

**Recommendation config** is controlled by env vars (`RECO_DEFAULT_N`, `RECO_MIN_REVIEWS`, `RECO_TRENDING_DAYS`, `RECO_COLLAB_MIN_SIMILARITY`).

---

## A/B Test Agent

### How it works

Traffic is split **per session** via a deterministic MD5 hash:

```
variant = "treatment" if MD5(experiment_id + ":" + session_id) % 1000 < split*1000
```

This means:
- The same session always sees the same variant (stable UX).
- Control and treatment are served **simultaneously** (no flip-flopping between deploys).
- No database round-trip is needed to determine the variant.

### Experiment definition

| Setting | Default | Env var |
|---|---|---|
| Enabled | `false` | `AB_TESTING_ENABLED` |
| Experiment ID | `exp_reco_v1` | `AB_EXPERIMENT_ID` |
| Traffic split (→ treatment) | `0.5` | `AB_TRAFFIC_SPLIT` |

**Control**: collaborative-filtering personalisation + velocity-based trending
**Treatment**: best-sellers replaces both personalised and trending sections

### New API endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/events` | Ingest a browser analytics event |
| `GET` | `/api/ab/variant?session_id=…` | Get the assigned variant for a session |
| `GET` | `/api/ab/config` | Experiment metadata |
| `GET` | `/api/ab/results` | Full statistical analysis (primary + secondary metrics, strategy breakdown, time series) |
| `GET` | `/dashboard` | Interactive HTML dashboard (Chart.js, auto-refreshes every 30 s) |

### Statistical tests (`backend/stats.py`)

- **Two-proportion z-test** — primary significance test (two-sided)
- **Wilson score confidence interval** — per-variant 95% CI on conversion rate
- **Cohen's h** — effect size for proportions (negligible / small / medium / large)
- **Bayesian Monte Carlo** — P(θ_treatment > θ_control) via Beta posteriors (10 k samples)
- **Power analysis** — required sample size per variant given MDE = 2 pp, α = 0.05, power = 0.80

### Metrics tracked

| Metric | Definition |
|---|---|
| `add_to_cart_rate` (**primary**) | sessions with ≥1 cart event / total sessions |
| `click_through_rate` | sessions with ≥1 product click / total sessions |
| `cart_per_click` | sessions with cart event / sessions with any click |

### Enabling the experiment

1. Set env vars on Render:
   ```
   AB_TESTING_ENABLED=true
   AB_EXPERIMENT_ID=exp_reco_v1
   AB_TRAFFIC_SPLIT=0.5
   ```
2. Deploy. Traffic is split immediately — no code change required.
3. Monitor at `https://<your-render-url>/dashboard`.

### Reading results

Visit `/dashboard` for a live view.  Raw JSON is at `/api/ab/results`.

**Significance**: p < 0.05 (two-sided) AND absolute lift ≥ 2 pp → declare a winner.
**Underpowered warning**: shown when either variant has fewer sessions than the computed required sample size.

### `ab_events` table schema

```sql
id           BIGSERIAL PRIMARY KEY
session_id   VARCHAR(120) NOT NULL
user_id      VARCHAR(120)
variant      VARCHAR(20)  NOT NULL     -- 'control' | 'treatment'
event_type   VARCHAR(60)  NOT NULL     -- 'landing_page_view' | 'product_click' | 'add_to_cart' | …
product_id   VARCHAR(30)
product_name VARCHAR(255)
category     VARCHAR(80)
strategy     VARCHAR(100)             -- recommendation strategy that led to the click
page_url     TEXT
referrer     TEXT
created_at   TIMESTAMPTZ DEFAULT NOW()
```
