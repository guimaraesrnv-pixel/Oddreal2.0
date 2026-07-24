"""
OddReal 2.0
Analisador Principal
"""

from __future__ import annotations

from typing import Dict, List

from oddsengine.odds import odds_engine
from modules.logger import info


class Analyzer:
    """
    Responsável por processar todos os eventos
    utilizando o OddsEngine.
    """

    def __init__(self):

        info("Analyzer iniciado.")

    def analyze(
        self,
        events: List[Dict]
    ) -> List[Dict]:

        analyses = []

        for event in events:

            try:

                analysis = odds_engine.analyze_event(
                    event
                )

                analyses.append(
                    analysis
                )

            except Exception as e:

                info(
                    f"Erro ao analisar evento: {e}"
                )

        return analyses

    def best_opportunity(
        self,
        analyses: List[Dict]
    ) -> Dict | None:

        if not analyses:

            return None

        return max(

            analyses,

            key=lambda x: x.get(
                "oddreal_index",
                0
            )

        )

    def value_bets(
        self,
        analyses: List[Dict]
    ) -> List[Dict]:

        return [

            analysis

            for analysis in analyses

            if analysis.get(
                "is_value_bet",
                False
            )

        ]


analyzer = Analyzer()
