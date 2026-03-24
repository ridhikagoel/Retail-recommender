import os

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.recommender import (
    personalized_for_you, customers_also_bought, best_sellers,
    new_arrivals, flash_deals, trending_now, because_you_viewed,
    complete_the_look, frequently_bought_together, editorial_picks,
    high_margin_spotlight, price_drop_alerts, get_landing_page,
)
from backend.schemas import (
    RecommendedProduct, LandingPageResponse, HealthResponse,
)
from backend.cache import RedisCache, get_cache, make_key
from backend.config import (
    RECO_DEFAULT_N, AB_TESTING_ENABLED, AB_TEST_VARIANT,
)

app = FastAPI(title="Retail Recommendation Engine", version="1.0.0")

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
)
_allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── A/B routing helpers ───────────────────────────────────────────────────────

def _resolve_personalized(user_id: str, n: int) -> list[dict]:
    """treatment: fall back to best_sellers as the variant strategy."""
    if AB_TESTING_ENABLED and AB_TEST_VARIANT == "treatment":
        return best_sellers(n)
    return personalized_for_you(user_id, n)


def _resolve_trending(n: int, category: str | None) -> list[dict]:
    """treatment: use best_sellers (by velocity+rating) instead of trending."""
    if AB_TESTING_ENABLED and AB_TEST_VARIANT == "treatment":
        return best_sellers(n, category)
    return trending_now(n, category)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health(cache: RedisCache = Depends(get_cache)):
    return {
        "status": "ok",
        "cache": "connected" if cache.is_connected() else "unavailable",
        "db": "connected",
    }


@app.get("/api/landing-page", response_model=LandingPageResponse)
def landing_page(
    user_id: str = Query(default="current_user"),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("landing", user_id)
    if hit := cache.get(key):
        return hit
    result = {"user_id": user_id, "sections": get_landing_page(user_id)}
    cache.set(key, result)
    return result


@app.get("/api/reco/personalized", response_model=list[RecommendedProduct])
def reco_personalized(
    user_id: str = Query(default="current_user"),
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("personalized", user_id, n)
    if hit := cache.get(key):
        return hit
    result = _resolve_personalized(user_id, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/also-bought", response_model=list[RecommendedProduct])
def reco_also_bought(
    product_id: str,
    n: int = Query(default=6, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("also_bought", product_id, n)
    if hit := cache.get(key):
        return hit
    result = customers_also_bought(product_id, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/best-sellers", response_model=list[RecommendedProduct])
def reco_best_sellers(
    category: str | None = None,
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("best_sellers", category, n)
    if hit := cache.get(key):
        return hit
    result = best_sellers(n, category)
    cache.set(key, result)
    return result


@app.get("/api/reco/new-arrivals", response_model=list[RecommendedProduct])
def reco_new_arrivals(
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("new_arrivals", n)
    if hit := cache.get(key):
        return hit
    result = new_arrivals(n)
    cache.set(key, result)
    return result


@app.get("/api/reco/flash-deals", response_model=list[RecommendedProduct])
def reco_flash_deals(
    n: int = Query(default=6, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("flash_deals", n)
    if hit := cache.get(key):
        return hit
    result = flash_deals(n)
    cache.set(key, result)
    return result


@app.get("/api/reco/trending", response_model=list[RecommendedProduct])
def reco_trending(
    category: str | None = None,
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("trending", category, n)
    if hit := cache.get(key):
        return hit
    result = _resolve_trending(n, category)
    cache.set(key, result)
    return result


@app.get("/api/reco/because-you-viewed", response_model=list[RecommendedProduct])
def reco_because_viewed(
    product_id: str,
    n: int = Query(default=6, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("because_viewed", product_id, n)
    if hit := cache.get(key):
        return hit
    result = because_you_viewed(product_id, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/complete-the-look", response_model=list[RecommendedProduct])
def reco_complete(
    user_id: str = Query(default="current_user"),
    n: int = Query(default=6, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("complete_look", user_id, n)
    if hit := cache.get(key):
        return hit
    result = complete_the_look(user_id, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/bought-together", response_model=list[RecommendedProduct])
def reco_bought_together(
    product_id: str,
    n: int = Query(default=3, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("bought_together", product_id, n)
    if hit := cache.get(key):
        return hit
    result = frequently_bought_together(product_id, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/editorial")
def reco_editorial(
    theme: str | None = None,
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("editorial", theme, n)
    if hit := cache.get(key):
        return hit
    result = editorial_picks(theme, n)
    cache.set(key, result)
    return result


@app.get("/api/reco/best-value", response_model=list[RecommendedProduct])
def reco_best_value(
    n: int = Query(default=6, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("best_value", n)
    if hit := cache.get(key):
        return hit
    result = high_margin_spotlight(n)
    cache.set(key, result)
    return result


@app.get("/api/reco/price-drops", response_model=list[RecommendedProduct])
def reco_price_drops(
    min_pct: int = Query(default=10, ge=1),
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    key = make_key("price_drops", min_pct, n)
    if hit := cache.get(key):
        return hit
    result = price_drop_alerts(n, min_pct)
    cache.set(key, result)
    return result
