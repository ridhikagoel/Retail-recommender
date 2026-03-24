"""
Integration tests for all FastAPI routes.
- Redis is replaced with FakeCache (always a miss) via dependency override.
- Recommender functions are mocked to return a fixed stub product list,
  keeping tests fast and independent of in-memory data correctness.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.cache import get_cache

# ── Helpers ───────────────────────────────────────────────────────────────────

class FakeCache:
    """Cache that always reports a miss and discards all writes."""
    def get(self, key): return None
    def set(self, key, value, ttl=None): pass
    def delete(self, key): pass
    def is_connected(self): return False


class HitCache:
    """Cache that always returns the provided value (simulates a warm cache)."""
    def __init__(self, value):
        self._value = value
    def get(self, key): return self._value
    def set(self, key, value, ttl=None): pass
    def delete(self, key): pass
    def is_connected(self): return True


# A single stub product that satisfies the RecommendedProduct schema
STUB = {
    "id": "X001", "name": "Test Widget", "category": "Electronics",
    "subcategory": "Gadgets", "brand": "ACME", "price": 49.99,
    "original_price": 59.99, "rating": 4.3, "review_count": 88,
    "inventory": 50, "margin": 0.30, "image_url": None,
    "description": "A test product", "tags": ["test"],
    "recommendation_score": 0.75, "reason": "Test reason", "badge": "",
}


@pytest.fixture
def client():
    app.dependency_overrides[get_cache] = lambda: FakeCache()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["cache"] == "unavailable"   # FakeCache.is_connected() == False
    assert "db" in data


# ── /api/landing-page ─────────────────────────────────────────────────────────

def test_landing_page_shape(client):
    section = {
        "id": "trending", "title": "Trending", "subtitle": "Hot items",
        "strategy": "7day_velocity", "products": [STUB],
    }
    with patch("backend.main.get_landing_page", return_value=[section]):
        r = client.get("/api/landing-page?user_id=current_user")
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "current_user"
    assert isinstance(data["sections"], list)
    assert data["sections"][0]["id"] == "trending"


# ── /api/reco/personalized ────────────────────────────────────────────────────

def test_personalized_returns_list(client):
    with patch("backend.main.personalized_for_you", return_value=[STUB]):
        r = client.get("/api/reco/personalized?user_id=current_user&n=8")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── /api/reco/best-sellers ────────────────────────────────────────────────────

def test_best_sellers_passes_category_and_n(client):
    with patch("backend.main.best_sellers", return_value=[STUB]) as mock:
        r = client.get("/api/reco/best-sellers?category=Electronics&n=5")
    assert r.status_code == 200
    mock.assert_called_once_with(5, "Electronics")


def test_best_sellers_no_category(client):
    with patch("backend.main.best_sellers", return_value=[STUB]) as mock:
        r = client.get("/api/reco/best-sellers?n=3")
    assert r.status_code == 200
    mock.assert_called_once_with(3, None)


# ── /api/reco/also-bought ─────────────────────────────────────────────────────

def test_also_bought_missing_product_id_returns_422(client):
    r = client.get("/api/reco/also-bought")
    assert r.status_code == 422


def test_also_bought_with_product_id(client):
    with patch("backend.main.customers_also_bought", return_value=[STUB]):
        r = client.get("/api/reco/also-bought?product_id=E001&n=6")
    assert r.status_code == 200


# ── /api/reco/because-you-viewed ─────────────────────────────────────────────

def test_because_viewed_missing_product_id_returns_422(client):
    r = client.get("/api/reco/because-you-viewed")
    assert r.status_code == 422


# ── /api/reco/trending ────────────────────────────────────────────────────────

def test_trending_default_n(client):
    with patch("backend.main.trending_now", return_value=[STUB]):
        r = client.get("/api/reco/trending")
    assert r.status_code == 200


# ── /api/reco/flash-deals ─────────────────────────────────────────────────────

def test_flash_deals_returns_list(client):
    with patch("backend.main.flash_deals", return_value=[STUB]):
        r = client.get("/api/reco/flash-deals")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── /api/reco/editorial ───────────────────────────────────────────────────────

def test_editorial_no_theme_returns_dict(client):
    themed = {"Work From Home": [STUB], "Self Care": [STUB]}
    with patch("backend.main.editorial_picks", return_value=themed):
        r = client.get("/api/reco/editorial")
    assert r.status_code == 200
    assert "Work From Home" in r.json()


def test_editorial_with_theme(client):
    with patch("backend.main.editorial_picks", return_value=[STUB]):
        r = client.get("/api/reco/editorial?theme=Work+From+Home")
    assert r.status_code == 200


# ── /api/reco/price-drops ─────────────────────────────────────────────────────

def test_price_drops_min_pct_param(client):
    with patch("backend.main.price_drop_alerts", return_value=[STUB]) as mock:
        r = client.get("/api/reco/price-drops?min_pct=15&n=6")
    assert r.status_code == 200
    mock.assert_called_once_with(6, 15)


# ── Cache behaviour ───────────────────────────────────────────────────────────

def test_cache_hit_bypasses_recommender(client):
    """When cache returns a value the recommender must not be called."""
    app.dependency_overrides[get_cache] = lambda: HitCache([STUB])
    with patch("backend.main.best_sellers") as mock_reco:
        r = client.get("/api/reco/best-sellers?n=8")
    mock_reco.assert_not_called()
    assert r.status_code == 200
    app.dependency_overrides[get_cache] = lambda: FakeCache()


# ── A/B testing ───────────────────────────────────────────────────────────────

def test_ab_treatment_trending_routes_to_best_sellers(client):
    """With AB_TESTING_ENABLED=True and variant=treatment, trending uses best_sellers."""
    with patch("backend.main.AB_TESTING_ENABLED", True), \
         patch("backend.main.AB_TEST_VARIANT", "treatment"), \
         patch("backend.main.trending_now") as mock_control, \
         patch("backend.main.best_sellers", return_value=[STUB]) as mock_treatment:
        r = client.get("/api/reco/trending?n=8")
    assert r.status_code == 200
    mock_control.assert_not_called()
    mock_treatment.assert_called()
