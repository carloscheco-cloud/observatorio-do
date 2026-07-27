import json
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> bytes | None: ...

    @abstractmethod
    def set(self, key: str, value: bytes, ttl: int) -> None: ...

    @abstractmethod
    def invalidate(self, prefix: str) -> None: ...


class InMemoryCache(CacheBackend):
    def __init__(self) -> None:
        self._values: dict[str, tuple[float, bytes]] = {}

    def get(self, key: str) -> bytes | None:
        item = self._values.get(key)
        if item is None:
            return None
        expires, value = item
        if expires < time.monotonic():
            self._values.pop(key, None)
            return None
        return value

    def set(self, key: str, value: bytes, ttl: int) -> None:
        self._values[key] = (time.monotonic() + ttl, value)

    def invalidate(self, prefix: str) -> None:
        for key in [item for item in self._values if item.startswith(prefix)]:
            self._values.pop(key, None)


class RedisCache(CacheBackend):
    """Adapter prepared for a redis client without making Redis mandatory."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def get(self, key: str) -> bytes | None:
        value: bytes | None = self.client.get(key)
        return value

    def set(self, key: str, value: bytes, ttl: int) -> None:
        self.client.setex(key, ttl, value)

    def invalidate(self, prefix: str) -> None:
        for key in self.client.scan_iter(f"{prefix}*"):
            self.client.delete(key)


cache: CacheBackend = InMemoryCache()


def cached_json(key: str, ttl: int, factory: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    existing = cache.get(key)
    if existing is not None:
        value: dict[str, Any] = json.loads(existing)
        return value
    value = factory()
    cache.set(key, json.dumps(value, default=str).encode(), ttl)
    return value
