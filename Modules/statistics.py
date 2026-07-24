"""
OddReal 2.0
Módulo de Estatísticas
"""

from __future__ import annotations

from typing import Dict, List


class StatisticsManager:
    """
    Responsável pelos cálculos estatísticos
    utilizados em todo o sistema.
    """

    def total_events(self, events: List[Dict]) -> int:
        return len(events)

    def average_odd(self, events: List[Dict]) -> float:

        odds = []

        for event in events:

            value = event.get("average_odd")

            if isinstance(value, (int, float)):
                odds.append(value)

        if not odds:
            return 0.0

        return round(sum(odds) / len(odds), 2)

    def highest_odd(self, events: List[Dict]) -> float:

        highest = 0.0

        for event in events:

            odd = (
                event.get("best_odd", {})
                .get("odd", 0)
            )

            if odd > highest:
                highest = odd

        return highest

    def confidence_average(
        self,
        events: List[Dict]
    ) -> float:

        scores = []

        for event in events:

            confidence = event.get("confidence")

            if isinstance(confidence, (int, float)):
                scores.append(confidence)

        if not scores:
            return 0.0

        return round(sum(scores) / len(scores), 2)

    def leagues(
        self,
        events: List[Dict]
    ) -> Dict:

        leagues = {}

        for event in events:

            league = event.get("league", "Desconhecida")

            leagues[league] = (
                leagues.get(league, 0) + 1
            )

        return leagues

    def summary(
        self,
        events: List[Dict]
    ) -> Dict:

        return {

            "total_events":
                self.total_events(events),

            "average_odd":
                self.average_odd(events),

            "highest_odd":
                self.highest_odd(events),

            "average_confidence":
                self.confidence_average(events),

            "leagues":
                self.leagues(events)

        }


statistics = StatisticsManager()
