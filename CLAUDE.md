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

data/
  products.py     # product data models / DB access layer
  seed_db.py      # one-time script to populate PostgreSQL with sample data

tests/
  test_strategies.py  # unit tests for recommender logic
  test_api.py         # integration tests against the FastAPI app via httpx
```

**Request flow**: FastAPI route → check Redis cache → if miss, run recommender strategy → write result to cache → return response.

**Recommendation config** is controlled by env vars (`RECO_DEFAULT_N`, `RECO_MIN_REVIEWS`, `RECO_TRENDING_DAYS`, `RECO_COLLAB_MIN_SIMILARITY`). A/B testing variant is selected via `AB_TEST_VARIANT` env var.
