"""
All 12 recommendation strategies.
Each function returns list[dict] — products with score + reason fields.
All public functions should have @cached_reco(ttl=900) in production.
"""

import math
import sys
import os
from collections import defaultdict

# Make sure data/ is importable from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.products import (
    PRODUCTS, PURCHASE_HISTORY, TRENDING_DATA,
    NEW_ARRIVALS, FLASH_DEALS, EDITORIAL_PICKS
)
from backend.config import RECO_MIN_SIMILARITY, MIN_FLASH_MARGIN


# ── Helpers ───────────────────────────────────────────────────────────

def _get(pid: str) -> dict | None:
    return next((p for p in PRODUCTS if p["id"] == pid), None)

def _by_ids(ids: list[str]) -> list[dict]:
    return [p for p in PRODUCTS if p["id"] in ids]

def _discount_pct(p: dict) -> int:
    if p["original_price"] > p["price"]:
        return round((1 - p["price"] / p["original_price"]) * 100)
    return 0

def _wilson(rating: float, n: int) -> float:
    """Wilson Lower Bound at 95% confidence."""
    if n == 0:
        return 0.0
    z = 1.96
    p = rating / 5.0
    denom  = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    return (centre - margin) / denom

def _enrich(p: dict, score: float, reason: str, badge: str = "") -> dict:
    return {**p, "recommendation_score": round(score, 3),
            "reason": reason, "badge": badge}


# ── Strategy 1: Personalized For You ─────────────────────────────────
# User-User Collaborative Filtering — Jaccard similarity

def personalized_for_you(user_id: str = "current_user", n: int = 8) -> list[dict]:
    current = set(PURCHASE_HISTORY.get(user_id, []))
    if not current:
        return best_sellers(n)          # cold-start fallback

    scores: dict[str, float] = defaultdict(float)
    for other_id, other_items in PURCHASE_HISTORY.items():
        if other_id == user_id:
            continue
        other = set(other_items)
        union  = len(current | other)
        sim    = len(current & other) / union if union else 0
        if sim >= RECO_MIN_SIMILARITY:
            for pid in other - current:
                scores[pid] += sim

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for pid, score in ranked[:n]:
        p = _get(pid)
        if p:
            result.append(_enrich(p, score, "Based on your purchase history"))
    return result


# ── Strategy 2: Customers Also Bought ────────────────────────────────
# Item-Item Collaborative Filtering — co-purchase co-occurrence

def customers_also_bought(product_id: str, n: int = 6) -> list[dict]:
    anchor_baskets = sum(
        1 for items in PURCHASE_HISTORY.values() if product_id in items
    )
    if anchor_baskets == 0:
        return []

    co: dict[str, int] = defaultdict(int)
    for items in PURCHASE_HISTORY.values():
        if product_id in items:
            for other in items:
                if other != product_id:
                    co[other] += 1

    scored = sorted(co.items(), key=lambda x: x[1], reverse=True)
    anchor = _get(product_id)
    result = []
    for pid, count in scored[:n]:
        p = _get(pid)
        if p:
            name = anchor["name"].split()[0] if anchor else "this item"
            score = count / anchor_baskets
            result.append(_enrich(p, score,
                f"Customers who bought {name} also bought this"))
    return result


# ── Strategy 3: Best Sellers ──────────────────────────────────────────
# Wilson Lower Bound rating + normalized 7-day sales velocity

def best_sellers(n: int = 8, category: str | None = None) -> list[dict]:
    products = [p for p in PRODUCTS
                if category is None or p["category"] == category]
    max_sales = max(TRENDING_DATA.values(), default=1)
    scored = []
    for p in products:
        r = _wilson(p["rating"], p["review_count"])
        s = TRENDING_DATA.get(p["id"], 0) / max_sales
        scored.append((p, 0.4 * r + 0.6 * s))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [_enrich(p, sc, "Top seller this week") for p, sc in scored[:n]]


# ── Strategy 4: New Arrivals ──────────────────────────────────────────
# Recency base score + early momentum boost

def new_arrivals(n: int = 8) -> list[dict]:
    new_prods = [p for p in PRODUCTS if p["id"] in NEW_ARRIVALS]
    max_sales = max(TRENDING_DATA.values(), default=1)
    scored = []
    for p in new_prods:
        momentum = TRENDING_DATA.get(p["id"], 0) / max_sales
        score    = 0.5 + 0.4 * momentum
        scored.append((p, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [_enrich(p, sc, "Just arrived", "NEW") for p, sc in scored[:n]]


# ── Strategy 5: Flash Deals ───────────────────────────────────────────
# Margin-aware urgency scoring (ends-soon + discount depth)

def flash_deals(n: int = 6) -> list[dict]:
    result = []
    for pid, deal in FLASH_DEALS.items():
        p = _get(pid)
        if not p or p["margin"] < MIN_FLASH_MARGIN:
            continue
        urgency  = 1 / (deal["ends_hours"] + 0.5)
        discount = deal["discount_pct"] / 100
        score    = 0.5 * urgency + 0.5 * discount
        enriched = _enrich(
            p, score,
            f"🔥 {deal['discount_pct']}% off — ends in {deal['ends_hours']}h",
            "FLASH DEAL"
        )
        enriched["flash_discount_pct"] = deal["discount_pct"]
        enriched["ends_in_hours"]      = deal["ends_hours"]
        result.append(enriched)
    return sorted(result, key=lambda x: x["recommendation_score"],
                  reverse=True)[:n]


# ── Strategy 6: Trending Right Now ───────────────────────────────────
# 7-day sliding window velocity, penalised for near-OOS inventory

def trending_now(n: int = 8, category: str | None = None) -> list[dict]:
    products  = [p for p in PRODUCTS
                 if category is None or p["category"] == category]
    max_sales = max(TRENDING_DATA.values(), default=1)
    scored = []
    for p in products:
        velocity         = TRENDING_DATA.get(p["id"], 0) / max_sales
        inventory_factor = min(1.0, p["inventory"] / 50)
        score            = velocity * inventory_factor
        if score > 0:
            scored.append((p, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [_enrich(p, sc, "Trending this week", "🔥 HOT")
            for p, sc in scored[:n]]


# ── Strategy 7: Because You Viewed ───────────────────────────────────
# Content-based filtering — Jaccard on tag + category + brand vectors

def because_you_viewed(product_id: str, n: int = 6) -> list[dict]:
    anchor = _get(product_id)
    if not anchor:
        return []
    anchor_vec = set(anchor["tags"]
                     + [anchor["category"].lower(),
                        anchor["subcategory"].lower(),
                        anchor["brand"].lower()])
    scored = []
    for p in PRODUCTS:
        if p["id"] == product_id:
            continue
        p_vec = set(p["tags"]
                    + [p["category"].lower(),
                       p["subcategory"].lower(),
                       p["brand"].lower()])
        union = len(anchor_vec | p_vec)
        sim   = len(anchor_vec & p_vec) / union if union else 0
        if p["subcategory"] == anchor["subcategory"]:
            sim *= 1.4
        if p["brand"] == anchor["brand"]:
            sim *= 1.2
        if sim > 0:
            scored.append((p, sim))
    scored.sort(key=lambda x: x[1], reverse=True)
    label = " ".join(anchor["name"].split()[:2])
    return [_enrich(p, sc, f"Similar to {label}") for p, sc in scored[:n]]


# ── Strategy 8: Complete The Look ────────────────────────────────────
# Cross-category affinity — recommend from complementary categories

CROSS_CATEGORY_MAP: dict[str, list[str]] = {
    "Electronics": ["Home", "Beauty"],
    "Home":        ["Grocery", "Beauty"],
    "Clothing":    ["Beauty", "Grocery"],
    "Toys":        ["Grocery", "Clothing"],
    "Beauty":      ["Clothing", "Grocery"],
    "Grocery":     ["Home", "Beauty"],
}

def complete_the_look(user_id: str = "current_user", n: int = 6) -> list[dict]:
    purchased = set(PURCHASE_HISTORY.get(user_id, []))
    bought_cats = {_get(pid)["category"]
                   for pid in purchased if _get(pid)}
    cross_cats: set[str] = set()
    for cat in bought_cats:
        cross_cats.update(CROSS_CATEGORY_MAP.get(cat, []))
    cross_cats -= bought_cats

    candidates = [p for p in PRODUCTS
                  if p["category"] in cross_cats
                  and p["id"] not in purchased]
    candidates.sort(
        key=lambda p: p["rating"] * math.log(p["review_count"] + 1),
        reverse=True
    )
    return [_enrich(p, round(p["rating"] / 5, 2),
                    "Complete your setup") for p in candidates[:n]]


# ── Strategy 9: Frequently Bought Together ───────────────────────────
# Apriori-lite — Lift score = P(A∩B) / (P(A) * P(B))

def frequently_bought_together(product_id: str, n: int = 3) -> list[dict]:
    total      = len(PURCHASE_HISTORY)
    anchor_ct  = sum(1 for items in PURCHASE_HISTORY.values()
                     if product_id in items)
    if anchor_ct == 0:
        return []
    p_anchor = anchor_ct / total

    co_counts: dict[str, int]    = defaultdict(int)
    item_counts: dict[str, int]  = defaultdict(int)
    for items in PURCHASE_HISTORY.values():
        for item in items:
            item_counts[item] += 1
        if product_id in items:
            for other in items:
                if other != product_id:
                    co_counts[other] += 1

    lifts = []
    for pid, co_count in co_counts.items():
        p_other = item_counts[pid] / total
        p_both  = co_count / total
        lift    = p_both / (p_anchor * p_other) if p_anchor * p_other else 0
        if lift > 1.0:
            lifts.append((pid, lift))
    lifts.sort(key=lambda x: x[1], reverse=True)

    anchor = _get(product_id)
    result = []
    for pid, lift in lifts[:n]:
        p = _get(pid)
        if p:
            name = anchor["name"].split()[0] if anchor else "this item"
            result.append(_enrich(p, round(lift / 5, 3),
                f"Frequently bought with {name}"))
    return result


# ── Strategy 10: Editorial Picks ─────────────────────────────────────
# Human curation + machine re-rank by rating × log(reviews)

def editorial_picks(theme: str | None = None, n: int = 8) -> list[dict]:
    def _rank(ids: list[str]) -> list[dict]:
        prods = _by_ids(ids)
        prods.sort(
            key=lambda p: p["rating"] * math.log(p["review_count"] + 1),
            reverse=True
        )
        return [_enrich(p, round(p["rating"] / 5, 2),
                        f"Curated: {theme or 'Editor pick'}")
                for p in prods[:n]]

    if theme and theme in EDITORIAL_PICKS:
        return _rank(EDITORIAL_PICKS[theme])

    # Return all themes as a dict if no theme specified
    return {t: _rank(ids) for t, ids in EDITORIAL_PICKS.items()}


# ── Strategy 11: High Margin Spotlight ───────────────────────────────
# margin × rating confidence — surfaces profitable + high-quality items

def high_margin_spotlight(n: int = 6) -> list[dict]:
    def _confidence(p: dict) -> float:
        return max(0.0, (p["rating"] - 4.0) / 1.0)

    scored = [
        (p, p["margin"] * (0.5 + 0.5 * _confidence(p)))
        for p in PRODUCTS
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [_enrich(p, sc, "Great value pick", "BEST VALUE")
            for p, sc in scored[:n]]


# ── Strategy 12: Price Drop Alerts ───────────────────────────────────
# Items with price reductions ≥ 10%, ranked by discount × rating

def price_drop_alerts(n: int = 8, min_pct: int = 10) -> list[dict]:
    candidates = [p for p in PRODUCTS if _discount_pct(p) >= min_pct]
    scored = [(p, _discount_pct(p) * p["rating"]) for p in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    result = []
    for p, sc in scored[:n]:
        d = _discount_pct(p)
        saving = round(p["original_price"] - p["price"], 2)
        enriched = _enrich(
            p, round(sc / 500, 3),
            f"Price dropped {d}% — save ${saving}",
            f"-{d}%"
        )
        enriched["discount_pct"] = d
        enriched["savings"]      = saving
        result.append(enriched)
    return result


# ── Landing Page Orchestrator ─────────────────────────────────────────
# Assembles all 12 sections for a single user. Called by GET /api/landing-page.

def get_landing_page(user_id: str = "current_user") -> list[dict]:
    recent = (PURCHASE_HISTORY.get(user_id) or ["E002"])[-1]
    sections = [
        {"id": "personalized",     "title": "Picked For You",
         "subtitle": "Based on your shopping history",
         "strategy": "user_user_collaborative_filtering",
         "products": personalized_for_you(user_id)},

        {"id": "flash_deals",      "title": "Flash Deals",
         "subtitle": "Today only — limited time offers",
         "strategy": "margin_aware_urgency",
         "products": flash_deals()},

        {"id": "trending",         "title": "Trending Right Now",
         "subtitle": "What everyone is buying this week",
         "strategy": "7day_velocity",
         "products": trending_now()},

        {"id": "because_viewed",   "title": "Because You Viewed",
         "subtitle": "More like what you have been browsing",
         "strategy": "content_based_tfidf",
         "products": because_you_viewed(recent)},

        {"id": "best_sellers",     "title": "Best Sellers",
         "subtitle": "Most loved by our customers",
         "strategy": "wilson_lower_bound",
         "products": best_sellers()},

        {"id": "price_drops",      "title": "Price Drops",
         "subtitle": "Prices cut since you last visited",
         "strategy": "price_delta_detection",
         "products": price_drop_alerts()},

        {"id": "new_arrivals",     "title": "New Arrivals",
         "subtitle": "Fresh picks just landed",
         "strategy": "recency_momentum",
         "products": new_arrivals()},

        {"id": "complete_look",    "title": "Complete Your Setup",
         "subtitle": "Products that go great with what you own",
         "strategy": "cross_category_affinity",
         "products": complete_the_look(user_id)},

        {"id": "best_value",       "title": "Best Value Picks",
         "subtitle": "High quality, great price",
         "strategy": "margin_rating_composite",
         "products": high_margin_spotlight()},

        {"id": "also_bought",      "title": "Customers Also Bought",
         "subtitle": "Popular with similar shoppers",
         "strategy": "item_item_collaborative_filtering",
         "products": customers_also_bought(recent)},

        {"id": "editorial",        "title": "Work From Home Essentials",
         "subtitle": "Curated by our editors",
         "strategy": "editorial_curation",
         "products": editorial_picks("Work From Home")},
    ]
    return [s for s in sections if s["products"]]