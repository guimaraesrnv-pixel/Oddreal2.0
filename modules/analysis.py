"""
OddReal 2.0
Módulo de Análise Principal
"""

from __future__ import annotations

from statistics import mean
from typing import Dict, List

from modules.logger import info, warning


class AnalysisEngine:
    """
    Responsável por gerar análises
    estatísticas básicas dos eventos.
    """

    def __init__(self):

        info("Analysis Engine inicializado.")

    def average_odds(
        self,
        bookmakers: List[Dict]
    ) -> float:

        odds = []

        for bookmaker in bookmakers:

            for market in bookmaker.get("markets", []):

                for outcome in market.get("outcomes", []):

                    price = outcome.get("price")

                    if isinstance(price, (int, float)):
                        odds.append(price)

        if not odds:

            return 0.0

        return round(mean(odds), 2)

    def best_odd(
        self,
        bookmakers: List[Dict]
    ) -> Dict:

        best = {
            "bookmaker": None,
            "team": None,
            "odd": 0.0
        }

        for bookmaker in bookmakers:

            for market in bookmaker.get("markets", []):

                for outcome in market.get("outcomes", []):

                    odd = outcome.get("price", 0)

                    if odd > best["odd"]:

                        best = {

                            "bookmaker": bookmaker.get("title"),

                            "team": outcome.get("name"),

                            "odd": odd

                        }

        return best

    def confidence_score(
        self,
        average_odd: float
    ) -> float:

        if average_odd <= 1.30:
            return 95

        if average_odd <= 1.60:
            return 85

        if average_odd <= 2.00:
            return 70

        if average_odd <= 3.00:
            return 55

        return 40

    def analyze_event(
        self,
        event: Dict
    ) -> Dict:

        bookmakers = event.get("bookmakers", [])

        avg = self.average_odds(bookmakers)

        best = self.best_odd(bookmakers)

        confidence = self.confidence_score(avg)

        analysis = {

            "event_id": event.get("id"),

            "home_team": event.get("home_team"),

            "away_team": event.get("away_team"),

            "average_odd": avg,

            "best_odd": best,

            "confidence": confidence

        }

        return analysis

    def analyze(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        if not events:

            warning("Nenhum evento recebido.")

            return []

        analyses = []

        for event in events:

            analyses.append(
                self.analyze_event(event)
            )

        info(f"{len(analyses)} análises concluídas.")

        return analyses


analysis_engine = AnalysisEngine()
