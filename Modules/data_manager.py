"""
OddReal 2.0
Gerenciador Central de Dados
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

from modules.logger import info, warning


class DataManager:
    """
    Responsável por padronizar, validar,
    organizar e preparar os dados para
    todo o sistema.
    """

    def __init__(self):

        self.last_update = None

    def normalize_events(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        normalized = []

        for event in events:

            normalized.append({

                "id": event.get("id"),

                "sport": event.get("sport_key"),

                "league": event.get("sport_title"),

                "home_team": event.get("home_team"),

                "away_team": event.get("away_team"),

                "commence_time": event.get("commence_time"),

                "bookmakers": event.get(
                    "bookmakers",
                    []
                )

            })

        info(
            f"{len(normalized)} eventos normalizados."
        )

        return normalized

    def remove_duplicates(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        unique = {}

        for event in events:

            unique[event["id"]] = event

        return list(unique.values())

    def sort_by_time(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        return sorted(
            events,
            key=lambda x: x["commence_time"]
        )

    def validate(
        self,
        events: List[Dict]
    ) -> bool:

        if not events:

            warning("Lista vazia.")

            return False

        return True

    def prepare(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        events = deepcopy(events)

        events = self.normalize_events(events)

        events = self.remove_duplicates(events)

        events = self.sort_by_time(events)

        self.last_update = datetime.now()

        return events

    def statistics(
        self,
        events: List[Dict]
    ) -> Dict[str, Any]:

        return {

            "total_events": len(events),

            "last_update": self.last_update

        }


data_manager = DataManager()
