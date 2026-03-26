from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

# Application
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("PORT", os.getenv("APP_PORT", 8000)))  # Render sets PORT
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "")

# PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB   = os.getenv("POSTGRES_DB", "recommender")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Append sslmode=require for Supabase / hosted Postgres (ignored by local PG)
_sslmode = os.getenv("POSTGRES_SSLMODE", "require")
DATABASE_URL = (
    f"postgresql://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={_sslmode}"
)

# Redis
REDIS_HOST     = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT     = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_TTL      = int(os.getenv("REDIS_TTL_SECONDS", 900))

# Recommendation engine
RECO_DEFAULT_N            = int(os.getenv("RECO_DEFAULT_N", 8))
RECO_MIN_REVIEWS          = int(os.getenv("RECO_MIN_REVIEWS", 10))
RECO_TRENDING_DAYS        = int(os.getenv("RECO_TRENDING_DAYS", 7))
RECO_MIN_SIMILARITY       = float(os.getenv("RECO_COLLAB_MIN_SIMILARITY", 0.1))
MIN_FLASH_MARGIN          = 0.10   # minimum margin % to surface a flash deal

# A/B testing
AB_TESTING_ENABLED = os.getenv("AB_TESTING_ENABLED", "false").lower() == "true"
AB_TEST_VARIANT    = os.getenv("AB_TEST_VARIANT", "control")