"""
OddReal 2.0
Analisador Principal

Responsável por:

- Executar o OddsEngine;
- Processar os eventos preparados pelo Pipeline;
- Separar oportunidades de Value Bet;
- Identificar a melhor oportunidade;
- Preservar informações de diagnóstico.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from oddsengine.odds import odds_engine
from modules.logger import info, error


class Analyzer:
    """
    Camada de análise entre o Pipeline e o OddsEngine.
    """

    def __init__(self) -> None:

        info(
            "Analyzer OddReal 2.0 iniciado."
        )

    # ==========================================================
    # ANÁLISE DE UM EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Analisa um único evento.

        Retorna None quando o evento não possui
        dados suficientes para análise.
        """

        if not isinstance(
            event,
            dict,
        ):

            return None

        try:

            result = (
                odds_engine.analyze_event(
                    event
                )
            )

            if not result:

                return None

            return result

        except Exception as exc:

            error(
                "Erro ao analisar evento: "
                f"{exc}"
            )

            return None

    # ==========================================================
    # ANÁLISE EM LOTE
    # ==========================================================

    def analyze(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Analisa todos os eventos recebidos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        analyses: List[
            Dict[str, Any]
        ] = []

        for event in events:

            result = self.analyze_event(
                event
            )

            if result is not None:

                analyses.append(
                    result
                )

        info(
            "Analyzer processou "
            f"{len(analyses)} eventos."
        )

        return analyses

    # ==========================================================
    # VALUE BETS
    # ==========================================================

    def value_bets(
        self,
        analyses: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Retorna somente as oportunidades classificadas
        pelo OddsEngine como Value Bet.
        """

        if not isinstance(
            analyses,
            list,
        ):

            return []

        opportunities = [

            analysis

            for analysis in analyses

            if isinstance(
                analysis,
                dict,
            )

            and analysis.get(
                "is_value_bet",
                False,
            )

        ]

        opportunities.sort(

            key=lambda item: float(
                item.get(
                    "oddreal_index",
                    0,
                )
                or 0
            ),

            reverse=True,

        )

        return opportunities

    # ==========================================================
    # MELHOR OPORTUNIDADE
    # ==========================================================

    def best_opportunity(
        self,
        analyses: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Identifica a oportunidade com maior Índice OddReal.

        A função não exige que seja Value Bet. Isso permite
        que o Dashboard mostre a melhor análise disponível
        mesmo quando nenhuma oportunidade ultrapassa o
        limite de Value Bet.
        """

        if not isinstance(
            analyses,
            list,
        ):

            return None

        valid = [

            item

            for item in analyses

            if isinstance(
                item,
                dict,
            )

        ]

        if not valid:

            return None

        return max(

            valid,

            key=lambda item: float(
                item.get(
                    "oddreal_index",
                    0,
                )
                or 0
            ),

        )

    # ==========================================================
    # MELHOR VALUE BET
    # ==========================================================

    def best_value_bet(
        self,
        analyses: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Identifica a melhor Value Bet pelo maior EV.
        """

        opportunities = self.value_bets(
            analyses
        )

        if not opportunities:

            return None

        return max(

            opportunities,

            key=lambda item: float(
                item.get(
                    "expected_value",
                    0,
                )
                or 0
            ),

        )

    # ==========================================================
    # ESTATÍSTICAS DO CONJUNTO
    # ==========================================================

    def summary(
        self,
        analyses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Gera um resumo quantitativo das análises.
        """

        if not isinstance(
            analyses,
            list,
        ):

            analyses = []

        valid = [

            item

            for item in analyses

            if isinstance(
                item,
                dict,
            )

        ]

        if not valid:

            return {

                "total": 0,

                "value_bets": 0,

                "average_index": 0.0,

                "average_ev": 0.0,

                "best_index": 0,

                "best_ev": 0.0,

            }

        indexes = [

            float(
                item.get(
                    "oddreal_index",
                    0,
                )
                or 0
            )

            for item in valid

        ]

        evs = [

            float(
                item.get(
                    "expected_value",
                    0,
                )
                or 0
            )

            for item in valid

        ]

        value_bets = self.value_bets(
            valid
        )

        return {

            "total": len(valid),

            "value_bets": len(
                value_bets
            ),

            "average_index": round(
                sum(indexes)
                / len(indexes),
                2,
            ),

            "average_ev": round(
                sum(evs)
                / len(evs),
                2,
            ),

            "best_index": max(
                indexes
            ),

            "best_ev": max(
                evs
            ),

        }


analyzer = Analyzer()
