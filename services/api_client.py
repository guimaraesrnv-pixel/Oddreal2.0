"""
OddReal 2.0
Cliente Oficial da The Odds API
"""

from __future__ import annotations

import requests
from typing import List, Dict

from config.settings import (
    API_KEY,
    BASE_URL,
    SPORT,
    REGIONS,
    MARKETS,
    ODDS_FORMAT
)

from modules.logger import info, error


class OddsAPIClient:

    def __init__(self):

        self.session = requests.Session()

    def get_events(self) -> List[Dict]:

        url = f"{BASE_URL}/{SPORT}/odds"

        params = {

            "apiKey": API_KEY,

            "regions": REGIONS,

            "markets": MARKETS,

            "oddsFormat": ODDS_FORMAT

        }

        try:

            response = self.session.get(

                url,

                params=params,

                timeout=30

            )

            response.raise_for_status()

            data = response.json()

            info(

                f"{len(data)} eventos carregados."

            )

            return data

        except Exception as e:

            error(

                f"Erro na API: {e}"

            )

            return []

    def health_check(self) -> bool:

        events = self.get_events()

        return len(events) > 0


api_client = OddsAPIClient()
