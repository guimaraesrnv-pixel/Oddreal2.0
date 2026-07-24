"""
OddReal 2.0
Motor Central de Inteligência Artificial
"""

from __future__ import annotations

from typing import Dict, List

from modules.analysis import analysis_engine
from modules.statistics import statistics
from modules.valuebet import valuebet_engine
from modules.logger import info


class AIEngine:
    """
    Responsável por coordenar toda a inteligência
    do OddReal.
    """

    def __init__(self):

        info("AI Engine iniciado.")

    def analyze(
        self,
        events: List[Dict]
    ) -> Dict:

        analyses = analysis_engine.analyze(events)

        stats = statistics.summary(analyses)

        opportunities = valuebet_engine.analyze(
            analyses
        )

        return {

            "analyses": analyses,

            "statistics": stats,

            "value_bets": opportunities,

            "recommendation": self.recommend(
                stats,
                opportunities
            )

        }

    def recommend(
        self,
        stats: Dict,
        opportunities: List[Dict]
    ) -> str:

        total = stats.get(
            "total_events",
            0
        )

        if total == 0:

            return (
                "Nenhum evento disponível "
                "para análise."
            )

        if len(opportunities) == 0:

            return (
                "Hoje não foram encontradas "
                "Value Bets interessantes."
            )

        if len(opportunities) <= 3:

            return (
                "Poucas oportunidades foram "
                "encontradas. Analise cada uma "
                "com cautela."
            )

        return (
            "Excelente rodada. Existem boas "
            "oportunidades para análise."
        )

    def explain(
        self,
        analysis: Dict
    ) -> str:

        home = analysis["home_team"]

        away = analysis["away_team"]

        confidence = analysis["confidence"]

        odd = analysis["best_odd"]["odd"]

        return (

            f"O jogo entre {home} e {away} "
            f"apresenta uma confiança de "
            f"{confidence}% e a melhor odd "
            f"encontrada foi {odd}."

        )


ai_engine = AIEngine()
