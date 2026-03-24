"""
Idempotent database seeder.
Run: python -m data.seed_db

Drops and recreates all tables, then populates them from the in-memory
constants in data/products.py. Safe to re-run at any time.
"""

import random
import sys
from datetime import datetime, timedelta, timezone

import psycopg2

from data.products import PRODUCTS, PURCHASE_HISTORY, FLASH_DEALS
from backend.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
)

random.seed(42)


# ── DDL ───────────────────────────────────────────────────────────────────────

DDL = """
DROP TABLE IF EXISTS flash_deals CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS purchases CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    id               VARCHAR(10)    PRIMARY KEY,
    name             VARCHAR(255)   NOT NULL,
    category         VARCHAR(50)    NOT NULL,
    subcategory      VARCHAR(100)   NOT NULL,
    brand            VARCHAR(100)   NOT NULL,
    price            NUMERIC(10,2)  NOT NULL,
    original_price   NUMERIC(10,2)  NOT NULL,
    rating           NUMERIC(3,2)   NOT NULL,
    review_count     INTEGER        NOT NULL DEFAULT 0,
    inventory        INTEGER        NOT NULL DEFAULT 100,
    margin           NUMERIC(5,4)   NOT NULL,
    image_url        TEXT,
    description      TEXT,
    tags             TEXT[]         NOT NULL DEFAULT '{}',
    is_new_arrival   BOOLEAN        NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE TABLE reviews (
    id          SERIAL       PRIMARY KEY,
    product_id  VARCHAR(10)  NOT NULL REFERENCES products(id),
    user_id     VARCHAR(50)  NOT NULL,
    rating      SMALLINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body        TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_user    ON reviews(user_id);

CREATE TABLE purchases (
    id           SERIAL       PRIMARY KEY,
    user_id      VARCHAR(50)  NOT NULL,
    product_id   VARCHAR(10)  NOT NULL REFERENCES products(id),
    quantity     SMALLINT     NOT NULL DEFAULT 1,
    purchased_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_purchases_user    ON purchases(user_id);
CREATE INDEX idx_purchases_product ON purchases(product_id);
CREATE INDEX idx_purchases_ts      ON purchases(purchased_at);

CREATE TABLE flash_deals (
    product_id   VARCHAR(10)  PRIMARY KEY REFERENCES products(id),
    discount_pct SMALLINT     NOT NULL,
    ends_at      TIMESTAMPTZ  NOT NULL
);
"""

_NEW_ARRIVAL_IDS = {"E008", "E009", "C005", "B006", "B007", "H007", "G006", "T006"}

_REVIEW_BODIES = [
    "Really happy with this purchase!", "Great quality for the price.",
    "Exceeded my expectations.", "Solid product, would recommend.",
    "Good but delivery took a while.", "Exactly as described.",
    "Five stars — will buy again.", "Works perfectly out of the box.",
    "My family loves it.", "Not bad, does the job.",
    "Excellent build quality.", "Fast shipping, great product.",
]


# ── Seeding functions ─────────────────────────────────────────────────────────

def create_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(DDL)
    print("  Schema created.")


def seed_products(conn) -> None:
    sql = """
        INSERT INTO products
            (id, name, category, subcategory, brand, price, original_price,
             rating, review_count, inventory, margin, image_url, description,
             tags, is_new_arrival)
        VALUES
            (%(id)s, %(name)s, %(category)s, %(subcategory)s, %(brand)s,
             %(price)s, %(original_price)s, %(rating)s, %(review_count)s,
             %(inventory)s, %(margin)s, %(image_url)s, %(description)s,
             %(tags)s, %(is_new_arrival)s)
    """
    with conn.cursor() as cur:
        for p in PRODUCTS:
            cur.execute(sql, {**p, "is_new_arrival": p["id"] in _NEW_ARRIVAL_IDS})
    print(f"  Inserted {len(PRODUCTS)} products.")


def seed_reviews(conn) -> None:
    now = datetime.now(tz=timezone.utc)
    sql = """
        INSERT INTO reviews (product_id, user_id, rating, body, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = []
    all_users = list(PURCHASE_HISTORY.keys())
    for p in PRODUCTS:
        count = p["review_count"]
        # Clamp to a reasonable seed range; high review_count products get more rows
        n = min(count, 40) if count >= 10 else max(count, 3)
        for i in range(n):
            user = all_users[i % len(all_users)]
            # Rating distribution biased toward product rating ± 0.5
            raw = p["rating"] + random.uniform(-0.5, 0.5)
            rating = max(1, min(5, round(raw)))
            days_ago = random.randint(0, 180)
            created_at = now - timedelta(days=days_ago)
            body = random.choice(_REVIEW_BODIES)
            rows.append((p["id"], user, rating, body, created_at))
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    print(f"  Inserted {len(rows)} reviews.")


def seed_purchases(conn) -> None:
    now = datetime.now(tz=timezone.utc)
    sql = """
        INSERT INTO purchases (user_id, product_id, quantity, purchased_at)
        VALUES (%s, %s, %s, %s)
    """
    rows = []
    for user_id, product_ids in PURCHASE_HISTORY.items():
        for pid in product_ids:
            days_ago = random.randint(0, 90)
            purchased_at = now - timedelta(days=days_ago)
            rows.append((user_id, pid, 1, purchased_at))
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    print(f"  Inserted {len(rows)} purchases.")


def seed_flash_deals(conn) -> None:
    now = datetime.now(tz=timezone.utc)
    sql = """
        INSERT INTO flash_deals (product_id, discount_pct, ends_at)
        VALUES (%s, %s, %s)
    """
    rows = [
        (pid, deal["discount_pct"], now + timedelta(hours=deal["ends_hours"]))
        for pid, deal in FLASH_DEALS.items()
    ]
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    print(f"  Inserted {len(rows)} flash deals.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Connecting to {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB} ...")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST, port=POSTGRES_PORT, dbname=POSTGRES_DB,
            user=POSTGRES_USER, password=POSTGRES_PASSWORD,
        )
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        create_schema(conn)
        seed_products(conn)
        seed_reviews(conn)
        seed_purchases(conn)
        seed_flash_deals(conn)
        conn.commit()
        print("Seed complete.")
    except Exception as e:
        conn.rollback()
        print(f"Seed failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
