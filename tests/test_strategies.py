"""
Unit tests for all recommender strategies.
No DB or Redis required — the 6 module-level data constants in
backend.recommender are patched with a small, controlled fixture.
"""

import pytest
from unittest.mock import patch

# ── Mock data ─────────────────────────────────────────────────────────────────

_PRODUCTS = [
    {"id": "P001", "name": "Alpha Laptop", "category": "Electronics", "subcategory": "Laptops",
     "brand": "TechCo", "price": 800.0, "original_price": 1000.0, "rating": 4.5,
     "review_count": 120, "inventory": 30, "margin": 0.35,
     "image_url": None, "description": "Great laptop", "tags": ["laptop", "work"]},

    {"id": "P002", "name": "Wireless Mouse", "category": "Electronics", "subcategory": "Peripherals",
     "brand": "TechCo", "price": 40.0, "original_price": 40.0, "rating": 4.2,
     "review_count": 55, "inventory": 200, "margin": 0.55,
     "image_url": None, "description": "Silent mouse", "tags": ["mouse", "wireless"]},

    {"id": "P003", "name": "Standing Desk", "category": "Home", "subcategory": "Furniture",
     "brand": "HomePro", "price": 350.0, "original_price": 420.0, "rating": 4.6,
     "review_count": 88, "inventory": 15, "margin": 0.30,
     "image_url": None, "description": "Adjustable desk", "tags": ["desk", "work", "ergonomic"]},

    {"id": "P004", "name": "Yoga Mat", "category": "Clothing", "subcategory": "Activewear",
     "brand": "FitBrand", "price": 30.0, "original_price": 40.0, "rating": 4.3,
     "review_count": 200, "inventory": 100, "margin": 0.50,
     "image_url": None, "description": "Non-slip mat", "tags": ["yoga", "fitness"]},

    {"id": "P005", "name": "Face Serum", "category": "Beauty", "subcategory": "Skincare",
     "brand": "GlowCo", "price": 25.0, "original_price": 35.0, "rating": 4.7,
     "review_count": 300, "inventory": 150, "margin": 0.70,
     "image_url": None, "description": "Brightening serum", "tags": ["skincare", "serum"]},

    {"id": "P006", "name": "Protein Bars 12pk", "category": "Grocery", "subcategory": "Snacks",
     "brand": "FuelUp", "price": 20.0, "original_price": 25.0, "rating": 4.1,
     "review_count": 400, "inventory": 500, "margin": 0.42,
     "image_url": None, "description": "High protein snack", "tags": ["protein", "snack"]},

    # New arrival — low review_count
    {"id": "P007", "name": "Smart Lamp", "category": "Home", "subcategory": "Lighting",
     "brand": "LightCo", "price": 45.0, "original_price": 45.0, "rating": 4.0,
     "review_count": 4, "inventory": 80, "margin": 0.48,
     "image_url": None, "description": "Voice-controlled lamp", "tags": ["lamp", "smart-home"]},

    # Low margin — should be excluded from flash deals
    {"id": "P008", "name": "Budget Cable", "category": "Electronics", "subcategory": "Accessories",
     "brand": "TechCo", "price": 5.0, "original_price": 8.0, "rating": 3.8,
     "review_count": 50, "inventory": 1000, "margin": 0.05,
     "image_url": None, "description": "USB cable", "tags": ["cable", "usb"]},
]

_PURCHASE_HISTORY = {
    "current_user": ["P001", "P003"],
    "user_02":      ["P001", "P002", "P004"],
    "user_03":      ["P002", "P003", "P005"],
    "user_04":      ["P004", "P005", "P006"],
    "user_05":      ["P001", "P006"],
}

_TRENDING_DATA = {
    "P001": 180, "P002": 90, "P003": 40,
    "P004": 110, "P005": 75, "P006": 60,
}

_NEW_ARRIVALS = ["P007"]

_FLASH_DEALS = {
    "P001": {"discount_pct": 20, "ends_hours": 5},   # margin 0.35 > 0.10 ✓
    "P008": {"discount_pct": 30, "ends_hours": 2},   # margin 0.05 < 0.10 ✗ excluded
}

_EDITORIAL_PICKS = {
    "Work From Home": ["P001", "P002", "P003"],
    "Wellness":       ["P004", "P005", "P006"],
}


@pytest.fixture(autouse=True)
def patch_data():
    with patch("backend.recommender.PRODUCTS",         _PRODUCTS), \
         patch("backend.recommender.PURCHASE_HISTORY", _PURCHASE_HISTORY), \
         patch("backend.recommender.TRENDING_DATA",    _TRENDING_DATA), \
         patch("backend.recommender.NEW_ARRIVALS",     _NEW_ARRIVALS), \
         patch("backend.recommender.FLASH_DEALS",      _FLASH_DEALS), \
         patch("backend.recommender.EDITORIAL_PICKS",  _EDITORIAL_PICKS):
        yield


# ── best_sellers ──────────────────────────────────────────────────────────────

def test_best_sellers_returns_n_results():
    from backend.recommender import best_sellers
    assert len(best_sellers(n=3)) == 3


def test_best_sellers_category_filter():
    from backend.recommender import best_sellers
    results = best_sellers(n=10, category="Electronics")
    assert results
    assert all(r["category"] == "Electronics" for r in results)


def test_best_sellers_score_descending():
    from backend.recommender import best_sellers
    scores = [r["recommendation_score"] for r in best_sellers(n=10)]
    assert scores == sorted(scores, reverse=True)


# ── personalized_for_you ──────────────────────────────────────────────────────

def test_personalized_cold_start_falls_back():
    from backend.recommender import personalized_for_you
    results = personalized_for_you(user_id="unknown_user", n=5)
    assert isinstance(results, list)
    assert all("recommendation_score" in r for r in results)


def test_personalized_excludes_purchased():
    from backend.recommender import personalized_for_you
    results = personalized_for_you(user_id="current_user", n=8)
    purchased = set(_PURCHASE_HISTORY["current_user"])
    assert {r["id"] for r in results}.isdisjoint(purchased)


# ── customers_also_bought ─────────────────────────────────────────────────────

def test_customers_also_bought_unknown_returns_empty():
    from backend.recommender import customers_also_bought
    assert customers_also_bought("DOES_NOT_EXIST") == []


def test_customers_also_bought_excludes_anchor():
    from backend.recommender import customers_also_bought
    results = customers_also_bought("P001", n=5)
    assert isinstance(results, list)
    assert all(r["id"] != "P001" for r in results)


# ── trending_now ──────────────────────────────────────────────────────────────

def test_trending_positive_scores():
    from backend.recommender import trending_now
    results = trending_now(n=5)
    assert results
    assert all(r["recommendation_score"] > 0 for r in results)


def test_trending_category_filter():
    from backend.recommender import trending_now
    results = trending_now(n=10, category="Electronics")
    assert results
    assert all(r["category"] == "Electronics" for r in results)


# ── flash_deals ───────────────────────────────────────────────────────────────

def test_flash_deals_excludes_low_margin():
    from backend.recommender import flash_deals
    results = flash_deals(n=10)
    ids = {r["id"] for r in results}
    assert "P008" not in ids  # margin 0.05 < MIN_FLASH_MARGIN


def test_flash_deals_includes_valid_deal():
    from backend.recommender import flash_deals
    results = flash_deals(n=10)
    assert any(r["id"] == "P001" for r in results)


# ── because_you_viewed ────────────────────────────────────────────────────────

def test_because_you_viewed_excludes_anchor():
    from backend.recommender import because_you_viewed
    results = because_you_viewed("P001", n=5)
    assert all(r["id"] != "P001" for r in results)


def test_because_you_viewed_unknown_returns_empty():
    from backend.recommender import because_you_viewed
    assert because_you_viewed("UNKNOWN") == []


# ── new_arrivals ──────────────────────────────────────────────────────────────

def test_new_arrivals_only_from_list():
    from backend.recommender import new_arrivals
    results = new_arrivals(n=10)
    assert results
    assert all(r["id"] in set(_NEW_ARRIVALS) for r in results)


# ── editorial_picks ───────────────────────────────────────────────────────────

def test_editorial_theme_returns_list():
    from backend.recommender import editorial_picks
    results = editorial_picks(theme="Work From Home", n=5)
    assert isinstance(results, list)
    assert all("recommendation_score" in r for r in results)


def test_editorial_no_theme_returns_dict():
    from backend.recommender import editorial_picks
    results = editorial_picks(theme=None, n=5)
    assert isinstance(results, dict)
    assert "Work From Home" in results
    assert "Wellness" in results


# ── price_drop_alerts ─────────────────────────────────────────────────────────

def test_price_drop_alerts_only_discounted():
    from backend.recommender import price_drop_alerts
    results = price_drop_alerts(n=10, min_pct=10)
    assert results
    assert all(r["original_price"] > r["price"] for r in results)


# ── high_margin_spotlight ─────────────────────────────────────────────────────

def test_high_margin_spotlight_score_descending():
    from backend.recommender import high_margin_spotlight
    scores = [r["recommendation_score"] for r in high_margin_spotlight(n=10)]
    assert scores == sorted(scores, reverse=True)


# ── get_landing_page ──────────────────────────────────────────────────────────

def test_landing_page_sections_structure():
    from backend.recommender import get_landing_page
    sections = get_landing_page(user_id="current_user")
    assert isinstance(sections, list)
    assert len(sections) > 0
    for s in sections:
        assert "id" in s
        assert "title" in s
        assert "products" in s
        assert isinstance(s["products"], list)
        assert len(s["products"]) > 0
