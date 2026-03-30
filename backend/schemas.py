from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    id: str
    name: str
    category: str
    subcategory: str
    brand: str
    price: float
    original_price: float
    rating: float
    review_count: int
    inventory: int
    margin: float
    image_url: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class RecommendedProduct(ProductBase):
    recommendation_score: float
    reason: str
    badge: str = ""
    # Flash deal extras (only present on flash_deals strategy results)
    flash_discount_pct: int | None = None
    ends_in_hours: int | None = None
    # Price drop extras (only present on price_drop_alerts results)
    discount_pct: int | None = None
    savings: float | None = None


class LandingPageSection(BaseModel):
    id: str
    title: str
    subtitle: str
    strategy: str
    products: list[RecommendedProduct]


class LandingPageResponse(BaseModel):
    user_id: str
    sections: list[LandingPageSection]


class HealthResponse(BaseModel):
    status: str
    cache: str  # "connected" | "unavailable"
    db: str     # "connected" | "unavailable"


# ── A/B Testing schemas ──────────────────────────────────────────────────────

class AnalyticsEvent(BaseModel):
    """Payload sent from the browser analytics tracker to POST /events."""
    session_id:   str
    user_id:      str | None = None
    variant:      str | None = None          # assigned by server if omitted
    event_type:   str                        # landing_page_view | product_click | add_to_cart | …
    product_id:   str | None = None
    product_name: str | None = None
    category:     str | None = None
    strategy:     str | None = None
    page_url:     str | None = None
    referrer:     str | None = None
    timestamp:    str | None = None          # ISO-8601


class VariantAssignment(BaseModel):
    session_id: str
    variant:    str           # "control" | "treatment"
    experiment_id: str
