"""
OddReal 2.0
Comunicação com The Odds API
"""

from __future__ import annotations

import requests
from typing import Dict, List, Optional

from config.settings import Settings
from modules.cache_manager import cache
from modules.logger import info, warning, error


class OddsAPI:

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):

        self.api_key = Settings.API_KEY
        self.timeout = 20

    def _request(
        self,
        endpoint: str,
        params: Optional[dict] = None
    ) -> dict:

        if params is None:
            params = {}

        params["apiKey"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        try:

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:

            error("Timeout ao acessar The Odds API.")
            return {}

        except requests.exceptions.HTTPError as exc:

            error(f"Erro HTTP: {exc}")
            return {}

        except Exception as exc:

            error(f"Erro inesperado: {exc}")
            return {}

    def get_sports(self) -> List[Dict]:

        cache_key = "sports"

        cached = cache.get(cache_key)

        if cached:

            info("Sports carregados do cache.")

            return cached

        info("Consultando lista de esportes.")

        sports = self._request("sports")

        cache.set(cache_key, sports, ttl=3600)

        return sports

    def get_events(
        self,
        sport: str
    ) -> List[Dict]:

        cache_key = f"events_{sport}"

        cached = cache.get(cache_key)

        if cached:

            return cached

        endpoint = f"sports/{sport}/odds"

        params = {
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }

        data = self._request(
            endpoint,
            params
        )

        cache.set(
            cache_key,
            data,
            ttl=120
        )

        return data

    def get_event_odds(
        self,
        sport: str,
        event_id: str
    ) -> Dict:

        endpoint = (
            f"sports/{sport}/events/"
            f"{event_id}/odds"
        )

        params = {
            "regions": "eu",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "decimal"
        }

        return self._request(
            endpoint,
            params
        )


api = OddsAPI()
