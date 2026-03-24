import json
import redis
from backend.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_TTL, AB_TESTING_ENABLED, AB_TEST_VARIANT


def make_key(strategy: str, *parts) -> str:
    """Build a deterministic cache key from strategy name and ordered params."""
    variant = AB_TEST_VARIANT if AB_TESTING_ENABLED else "control"
    segments = [str(p) if p is not None else "all" for p in parts]
    return f"reco:{strategy}:{':'.join(segments)}:{variant}"


class RedisCache:
    def __init__(self) -> None:
        self._client: redis.Redis | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            self._client.ping()
        except Exception:
            self._client = None  # fail-open: API still works without Redis

    def get(self, key: str) -> list | dict | None:
        """Return deserialized value or None on miss/error."""
        if self._client is None:
            return None
        try:
            raw = self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def set(self, key: str, value: list | dict, ttl: int = REDIS_TTL) -> None:
        """Serialize and store value with TTL. Silently fails on error."""
        if self._client is None:
            return
        try:
            self._client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def delete(self, key: str) -> None:
        if self._client is None:
            return
        try:
            self._client.delete(key)
        except Exception:
            pass

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False


# Module-level singleton used via FastAPI dependency injection
cache = RedisCache()


def get_cache() -> RedisCache:
    return cache
