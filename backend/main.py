import os

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.recommender import (
    personalized_for_you, customers_also_bought, best_sellers,
    new_arrivals, flash_deals, trending_now, because_you_viewed,
    complete_the_look, frequently_bought_together, editorial_picks,
    high_margin_spotlight, price_drop_alerts, get_landing_page,
)
from backend.schemas import (
    RecommendedProduct, LandingPageResponse, HealthResponse,
    AnalyticsEvent, VariantAssignment,
)
from backend.cache import RedisCache, get_cache, make_key
from backend.config import RECO_DEFAULT_N
from backend.ab_testing import assign_variant, EXPERIMENT_META
from backend import analytics, stats
from backend.dashboard import DASHBOARD_HTML

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


# ── Startup ────────────────────────────────────────────────────────────────

@app.on_event("startup")
def _startup():
    analytics.init_events_table()


# ── A/B routing helpers ────────────────────────────────────────────────────

def _resolve_personalized(user_id: str, n: int, variant: str) -> list[dict]:
    """treatment: fall back to best_sellers as the variant strategy."""
    if variant == "treatment":
        return best_sellers(n)
    return personalized_for_you(user_id, n)


def _resolve_trending(n: int, category: str | None, variant: str) -> list[dict]:
    """treatment: use best_sellers (by velocity+rating) instead of trending."""
    if variant == "treatment":
        return best_sellers(n, category)
    return trending_now(n, category)


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health(cache: RedisCache = Depends(get_cache)):
    try:
        import psycopg2
        from backend.config import DATABASE_URL
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"unavailable: {e}"
    return {
        "status": "ok",
        "cache": "connected" if cache.is_connected() else "unavailable",
        "db": db_status,
    }


@app.get("/debug/db", include_in_schema=False)
def debug_db():
    """Diagnostic endpoint — shows DB connection status and event count."""
    import psycopg2
    from backend.config import DATABASE_URL
    result = {"database_url_prefix": DATABASE_URL[:40] + "…", "table_exists": False,
              "row_count": 0, "error": None}
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        cur  = conn.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='ab_events')")
        result["table_exists"] = cur.fetchone()[0]
        if result["table_exists"]:
            cur.execute("SELECT COUNT(*) FROM ab_events")
            result["row_count"] = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        result["error"] = str(e)
    return result


@app.get("/api/landing-page", response_model=LandingPageResponse)
def landing_page(
    user_id:    str = Query(default="current_user"),
    session_id: str = Query(default=""),
    cache: RedisCache = Depends(get_cache),
):
    variant = assign_variant(session_id) if session_id else "control"
    key = make_key("landing", user_id, variant)
    if hit := cache.get(key):
        return hit
    result = {"user_id": user_id, "sections": get_landing_page(user_id)}
    cache.set(key, result)
    return result


@app.get("/api/reco/personalized", response_model=list[RecommendedProduct])
def reco_personalized(
    user_id:    str = Query(default="current_user"),
    session_id: str = Query(default=""),
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    variant = assign_variant(session_id) if session_id else "control"
    key = make_key("personalized", user_id, n, variant)
    if hit := cache.get(key):
        return hit
    result = _resolve_personalized(user_id, n, variant)
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
    category:   str | None = None,
    session_id: str = Query(default=""),
    n: int = Query(default=RECO_DEFAULT_N, ge=1, le=50),
    cache: RedisCache = Depends(get_cache),
):
    variant = assign_variant(session_id) if session_id else "control"
    key = make_key("trending", category, n, variant)
    if hit := cache.get(key):
        return hit
    result = _resolve_trending(n, category, variant)
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


# ── A/B Testing endpoints ──────────────────────────────────────────────────

@app.post("/events", status_code=204)
def ingest_event(event: AnalyticsEvent):
    """
    Receive a browser analytics event and persist it with the server-side
    variant assignment for that session.
    """
    data = event.model_dump()
    # Always assign variant server-side (client-supplied value is advisory)
    data["variant"] = assign_variant(event.session_id)
    analytics.store_event(data)


@app.get("/api/ab/variant", response_model=VariantAssignment)
def get_variant(session_id: str = Query(...)):
    """
    Return the variant assigned to a session.  Called by the analytics tracker
    on page load so the client can tag events with the correct variant.
    """
    return VariantAssignment(
        session_id=session_id,
        variant=assign_variant(session_id),
        experiment_id=EXPERIMENT_META["id"],
    )


@app.get("/api/ab/config")
def get_ab_config():
    """Return current experiment configuration."""
    return EXPERIMENT_META


@app.get("/api/ab/results")
def get_ab_results():
    """
    Full A/B test statistical analysis.

    Runs two-proportion z-tests on the primary (add-to-cart) and secondary
    (click-through, cart-per-click) metrics, adds Bayesian posterior
    probability, power analysis, and practical-significance interpretation.
    """
    variant_metrics   = analytics.get_variant_metrics()
    strategy_breakdown = analytics.get_strategy_breakdown()
    time_series       = analytics.get_daily_time_series(14)
    top_products      = analytics.get_top_converting_products(10)

    analysis = stats.analyse_experiment(variant_metrics)
    pm       = analysis["primary_metric"]

    return {
        "experiment":        EXPERIMENT_META,
        "primary_metric":    pm,
        "secondary_metrics": analysis["secondary_metrics"],
        "strategy_breakdown": strategy_breakdown,
        "time_series":       time_series,
        "top_converting_products": top_products,
        "raw_variant_metrics":     variant_metrics,
    }


# ── Dashboard ──────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    """Serve the self-contained A/B test dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)
