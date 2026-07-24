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
        
    def risk_level(
        self,
        probability: float,
        ev: float
    ) -> str:

        if probability >= 75 and ev >= 10:
            return "Baixo"

        if probability >= 60 and ev >= 5:
            return "Moderado"

        return "Alto"

    def market_consensus(
        self,
        bookmakers: list
    ) -> float:

        if not bookmakers:
            return 0.0

        odds = []

        for bookmaker in bookmakers:

            odd = bookmaker.get("odd")

            if odd is not None:
                odds.append(odd)

        if not odds:
            return 0.0

        return round(sum(odds) / len(odds), 2)

    def market_variation(
        self,
        best_odd: float,
        average_odd: float
    ) -> float:

        if average_odd == 0:
            return 0

        return round(
            ((best_odd - average_odd) / average_odd) * 100,
            2
        )
        
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
        average_odd = self.market_consensus(
            event.get("bookmakers", [])
        )

        variation = self.market_variation(
            odd,
            average_odd
        )

        risk = self.risk_level(
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
            "average_odd": average_odd,

            "market_variation": variation,

            "risk": risk,
            "is_value_bet":
                ev > 5

        }


odds_engine = OddsEngine()
