"""
OddReal 2.0
Detector de Value Bets
"""

from __future__ import annotations

from typing import Dict, List

from modules.logger import info


class ValueBetEngine:
    """
    Responsável por identificar
    oportunidades de Value Bet.
    """

    def __init__(self):

        self.minimum_ev = 5.0

    def implied_probability(
        self,
        odd: float
    ) -> float:

        if odd <= 0:
            return 0

        return 100 / odd

    def expected_value(
        self,
        probability: float,
        odd: float
    ) -> float:

        return (
            probability * odd
        ) - 100

    def is_value_bet(
        self,
        probability: float,
        odd: float
    ) -> bool:

        ev = self.expected_value(
            probability,
            odd
        )

        return ev >= self.minimum_ev

    def analyze(
        self,
        analyses: List[Dict]
    ) -> List[Dict]:

        opportunities = []

        for event in analyses:

            odd = (
                event["best_odd"]
                .get("odd", 0)
            )

            probability = event.get(
                "confidence",
                0
            )

            ev = self.expected_value(
                probability,
                odd
            )

            if self.is_value_bet(
                probability,
                odd
            ):

                opportunities.append({

                    "event_id":
                        event["event_id"],

                    "home_team":
                        event["home_team"],

                    "away_team":
                        event["away_team"],

                    "odd":
                        odd,

                    "probability":
                        probability,

                    "expected_value":
                        round(ev, 2)

                })

        info(
            f"{len(opportunities)} "
            "Value Bets encontradas."
        )

        return opportunities


valuebet_engine = ValueBetEngine()
