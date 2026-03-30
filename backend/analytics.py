"""
Analytics layer — PostgreSQL event storage and A/B metrics queries.

The `ab_events` table is created on first startup (idempotent).
A fail-open pattern is used throughout: if the DB is unavailable, functions
log a warning and return empty results rather than raising.
"""

import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator

import psycopg2
import psycopg2.extras

from backend.config import DATABASE_URL

logger = logging.getLogger(__name__)

# ── DB connection ────────────────────────────────────────────────────────────

@contextmanager
def _conn() -> Generator:
    """Context manager that yields a committed/rolled-back psycopg2 connection."""
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        yield connection
        connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


# ── Schema init ──────────────────────────────────────────────────────────────

# Each statement is executed separately — psycopg2 cursor.execute() is
# unreliable with multiple semicolon-separated statements in one call.
_INIT_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS ab_events (
        id           BIGSERIAL    PRIMARY KEY,
        session_id   VARCHAR(120) NOT NULL,
        user_id      VARCHAR(120),
        variant      VARCHAR(20)  NOT NULL,
        event_type   VARCHAR(60)  NOT NULL,
        product_id   VARCHAR(30),
        product_name VARCHAR(255),
        category     VARCHAR(80),
        strategy     VARCHAR(100),
        page_url     TEXT,
        referrer     TEXT,
        created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ab_variant    ON ab_events (variant)",
    "CREATE INDEX IF NOT EXISTS idx_ab_session    ON ab_events (session_id)",
    "CREATE INDEX IF NOT EXISTS idx_ab_event_type ON ab_events (event_type)",
    "CREATE INDEX IF NOT EXISTS idx_ab_created_at ON ab_events (created_at)",
    "CREATE INDEX IF NOT EXISTS idx_ab_strategy   ON ab_events (strategy)",
]


def init_events_table() -> None:
    """Create the ab_events table and indexes if they don't already exist."""
    try:
        with _conn() as con:
            with con.cursor() as cur:
                for stmt in _INIT_STATEMENTS:
                    cur.execute(stmt)
        logger.info("ab_events table ready")
    except Exception as exc:
        logger.warning("Could not initialise ab_events table: %s", exc)


# ── Write ────────────────────────────────────────────────────────────────────

def store_event(event: dict) -> None:
    """
    Persist a single analytics event.

    Expected keys (all optional except session_id, variant, event_type):
        session_id, user_id, variant, event_type, product_id, product_name,
        category, strategy, page_url, referrer, timestamp (ISO string)
    """
    sql = """
    INSERT INTO ab_events
        (session_id, user_id, variant, event_type, product_id,
         product_name, category, strategy, page_url, referrer, created_at)
    VALUES
        (%(session_id)s, %(user_id)s, %(variant)s, %(event_type)s, %(product_id)s,
         %(product_name)s, %(category)s, %(strategy)s, %(page_url)s, %(referrer)s,
         %(created_at)s)
    """
    raw_ts = event.get("timestamp")
    try:
        created_at = datetime.fromisoformat(raw_ts) if raw_ts else datetime.now(timezone.utc)
    except ValueError:
        created_at = datetime.now(timezone.utc)

    params = {
        "session_id":   event.get("session_id", ""),
        "user_id":      event.get("user_id"),
        "variant":      event.get("variant", "control"),
        "event_type":   event.get("event_type", ""),
        "product_id":   event.get("product_id"),
        "product_name": event.get("product_name"),
        "category":     event.get("category"),
        "strategy":     event.get("strategy"),
        "page_url":     event.get("page_url"),
        "referrer":     event.get("referrer"),
        "created_at":   created_at,
    }
    try:
        with _conn() as con:
            with con.cursor() as cur:
                cur.execute(sql, params)
    except Exception as exc:
        logger.warning("Could not store event: %s", exc)


# ── Read ─────────────────────────────────────────────────────────────────────

def get_variant_metrics() -> dict:
    """
    Aggregate per-variant session and conversion counts.

    Returns
    -------
    {
      "control":   {"variant", "sessions", "landing_views",
                    "click_sessions", "cart_sessions"},
      "treatment": { … },
    }
    """
    sql = """
    SELECT
        variant,
        COUNT(DISTINCT session_id)                                              AS sessions,
        COUNT(*)        FILTER (WHERE event_type = 'landing_page_view')         AS landing_views,
        COUNT(DISTINCT session_id)
            FILTER (WHERE event_type = 'product_click')                         AS click_sessions,
        COUNT(DISTINCT session_id)
            FILTER (WHERE event_type = 'add_to_cart')                           AS cart_sessions
    FROM ab_events
    GROUP BY variant
    ORDER BY variant;
    """
    try:
        with _conn() as con:
            with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                return {row["variant"]: dict(row) for row in cur.fetchall()}
    except Exception as exc:
        logger.warning("Could not fetch variant metrics: %s", exc)
        return {}


def get_strategy_breakdown() -> list[dict]:
    """
    Click count per (variant, strategy), used for strategy-level CTR analysis.
    """
    sql = """
    SELECT
        variant,
        strategy,
        COUNT(*)                   AS clicks,
        COUNT(DISTINCT session_id) AS sessions
    FROM ab_events
    WHERE event_type = 'product_click'
      AND strategy   IS NOT NULL
    GROUP BY variant, strategy
    ORDER BY variant, clicks DESC;
    """
    try:
        with _conn() as con:
            with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(r) for r in cur.fetchall()]
    except Exception as exc:
        logger.warning("Could not fetch strategy breakdown: %s", exc)
        return []


def get_daily_time_series(days: int = 14) -> list[dict]:
    """
    Daily sessions + converting sessions per variant for the last N days.
    Each row: {variant, date (ISO string), sessions, cart_sessions}
    """
    sql = """
    SELECT
        variant,
        DATE(created_at AT TIME ZONE 'UTC')                                    AS date,
        COUNT(DISTINCT session_id)                                             AS sessions,
        COUNT(DISTINCT session_id)
            FILTER (WHERE event_type = 'add_to_cart')                          AS cart_sessions
    FROM ab_events
    WHERE created_at >= NOW() - (%(days)s || ' days')::INTERVAL
    GROUP BY variant, DATE(created_at AT TIME ZONE 'UTC')
    ORDER BY date, variant;
    """
    try:
        with _conn() as con:
            with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, {"days": days})
                return [
                    {**dict(r), "date": r["date"].isoformat()}
                    for r in cur.fetchall()
                ]
    except Exception as exc:
        logger.warning("Could not fetch time series: %s", exc)
        return []


def get_top_converting_products(limit: int = 10) -> list[dict]:
    """
    Products with the most add_to_cart events, broken down by variant.
    """
    sql = """
    SELECT
        variant,
        product_id,
        product_name,
        category,
        COUNT(*) AS cart_adds
    FROM ab_events
    WHERE event_type = 'add_to_cart'
      AND product_id IS NOT NULL
    GROUP BY variant, product_id, product_name, category
    ORDER BY cart_adds DESC
    LIMIT %(limit)s;
    """
    try:
        with _conn() as con:
            with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, {"limit": limit})
                return [dict(r) for r in cur.fetchall()]
    except Exception as exc:
        logger.warning("Could not fetch top products: %s", exc)
        return []
