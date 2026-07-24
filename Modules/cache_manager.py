"""
OddReal 2.0
Gerenciador de Cache
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional


class CacheManager:
    """
    Cache em memória com tempo de expiração (TTL).
    """

    def __init__(self):

        self._cache: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any, ttl: int = 300):

        self._cache[key] = {
            "value": value,
            "expires": time.time() + ttl
        }

    def get(self, key: str) -> Optional[Any]:

        item = self._cache.get(key)

        if item is None:
            return None

        if item["expires"] < time.time():

            del self._cache[key]
            return None

        return item["value"]

    def delete(self, key: str):

        if key in self._cache:
            del self._cache[key]

    def clear(self):

        self._cache.clear()

    def exists(self, key: str) -> bool:

        return self.get(key) is not None

    def size(self) -> int:

        return len(self._cache)

    def cleanup(self):

        now = time.time()

        expired = [
            key
            for key, value in self._cache.items()
            if value["expires"] < now
        ]

        for key in expired:
            del self._cache[key]


cache = CacheManager()
