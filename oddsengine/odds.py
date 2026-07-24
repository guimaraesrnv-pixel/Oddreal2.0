"""
OddReal 2.0
Motor de Cálculo de Odds
"""

from __future__ import annotations

from typing import Dict


class OddsEngine:

    def implied_probability(
        self,
        odd: float
    ) -> float:

        if odd <= 0:
            return 0.0

        return round(100 / odd, 2)

    def expected_value(
        self,
        probability: float,
        odd: float
    ) -> float:

        return round(
            (probability * odd) - 100,
            2
        )

    def oddreal_index(
        self,
        probability: float,
        ev: float
    ) -> int:

        score = probability

        if ev > 0:
            score += min(ev, 20)

        return max(
            0,
            min(
                int(score),
                100
            )
        )

    def confidence_level(
        self,
        index: int
    ) -> str:

        if index >= 85:
            return "Muito Alta"

        if index >= 70:
            return "Alta"

        if index >= 55:
            return "Média"

        return "Baixa"

    def analyze_event(
        self,
        event: Dict
    ) -> Dict:

        best = event["best_odd"]

        odd = best["odd"]

        probability = event.get(
            "confidence",
            self.implied_probability(odd)
        )

        ev = self.expected_value(
            probability,
            odd
        )

        index = self.oddreal_index(
            probability,
            ev
        )

        return {

            **event,

            "probability": probability,

            "expected_value": ev,

            "oddreal_index": index,

            "confidence_level":
                self.confidence_level(index),

            "is_value_bet":
                ev > 5

        }


odds_engine = OddsEngine()
