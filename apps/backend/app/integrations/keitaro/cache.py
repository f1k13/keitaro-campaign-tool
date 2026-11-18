# START_MODULE_CONTRACT
#   PURPOSE: Tiny in-process TTL cache for slow, rarely changing Keitaro list endpoints.
#   SCOPE: Per-process memory; single-flight per key so concurrent misses hit Keitaro once.
#   DEPENDS: none
#   LINKS: M-KEITARO-CLIENT, V-M-KEITARO-CLIENT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   TTLCache     - get_or_load(key, loader) with expiry, invalidate(key) with generation guard
#   keitaro_cache - process-wide instance used by KeitaroClient
# END_MODULE_MAP
import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        # bumped by invalidate(); a load started before an invalidation must not be stored
        self._generation: dict[str, int] = {}

    # START_CONTRACT: get_or_load
    #   PURPOSE: Return a fresh cached value or load it once (concurrent callers wait for one load).
    #   INPUTS: { key: str, ttl: float - seconds (<= 0 disables caching), loader: async () -> value }
    #   OUTPUTS: { cached or freshly loaded value }
    #   SIDE_EFFECTS: stores the value with expiry unless invalidate() ran during the load; errors not cached
    # END_CONTRACT: get_or_load
    async def get_or_load(self, key: str, ttl: float, loader: Callable[[], Awaitable[Any]]) -> Any:
        if ttl <= 0:
            return await loader()
        hit = self._data.get(key)
        if hit and hit[0] > time.monotonic():
            return hit[1]
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            hit = self._data.get(key)
            if hit and hit[0] > time.monotonic():
                return hit[1]
            generation = self._generation.get(key, 0)
            value = await loader()
            if self._generation.get(key, 0) == generation:
                self._data[key] = (time.monotonic() + ttl, value)
            return value

    def invalidate(self, key: str) -> None:
        self._generation[key] = self._generation.get(key, 0) + 1
        self._data.pop(key, None)


keitaro_cache = TTLCache()
