"""
OddReal 2.0
Motor de Value Bets

Arquivo:
oddsengine/value.py

Responsável por:
- Probabilidade implícita;
- Valor esperado (EV);
- Identificação de Value Bets;
- Classificação das oportunidades;
- Seleção da melhor Value Bet.

Não consulta API.
Não utiliza IA.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info


class ValueBetEngine:
    """
    Motor matemático de Value Bets.
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
    ) -> None:

        self.minimum_ev = float(
            minimum_ev
        )

        info(
            "ValueBetEngine OddReal 2.0 iniciado."
        )

    # ==========================================================
    # CONVERSÃO SEGURA
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            result = float(value)

            if result != result:
                return default

            return result

        except (
            TypeError,
            ValueError,
        ):

            return default

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    def implied_probability(
        self,
        odd: float,
    ) -> float:

        odd = self._safe_float(
            odd
        )

        if odd <= 0:
            return 0.0

        return 100.0 / odd

    # ==========================================================
    # EXPECTED VALUE
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula EV percentual.

        probability:
            probabilidade justa em 0-100.

        odd:
            odd decimal.

        Fórmula:

            EV = ((probabilidade / 100) * odd - 1) * 100

        Exemplo:

            probability = 15
            odd = 8

            EV = ((0.15 * 8) - 1) * 100
            EV = 20%
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if probability <= 0 or odd <= 0:
            return 0.0

        probability_decimal = (
            probability / 100.0
        )

        return round(
            (
                probability_decimal * odd
                - 1.0
            ) * 100.0,
            4,
        )

    # ==========================================================
    # VALUE BET
    # ==========================================================

    def is_value_bet(
        self,
        probability: float,
        odd: float,
    ) -> bool:

        ev = self.expected_value(
            probability,
            odd,
        )

        return ev >= self.minimum_ev

    # ==========================================================
    # CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def classify(
        expected_value: float,
    ) -> str:

        ev = float(
            expected_value
        )

        if ev >= 15:
            return "Excelente"

        if ev >= 10:
            return "Muito Forte"

        if ev >= 5:
            return "Value Bet"

        if ev > 0:
            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # ANALISAR
    # ==========================================================

    def analyze(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            analyses,
            list,
        ):
            return []

        opportunities: List[
            Dict[str, Any]
        ] = []

        for event in analyses:

            if not isinstance(
                event,
                dict,
            ):
                continue

            # --------------------------------------------------
            # ODD
            # --------------------------------------------------

            best_odd = event.get(
                "best_odd",
                {},
            )

            if not isinstance(
                best_odd,
                dict,
            ):
                best_odd = {}

            odd = self._safe_float(
                event.get(
                    "odd",
                    best_odd.get(
                        "odd",
                        0,
                    ),
                )
            )

            if odd <= 0:
                continue

            # --------------------------------------------------
            # PROBABILIDADE JUSTA
            # --------------------------------------------------

            probability = self._safe_float(
                event.get(
                    "probability",
                    event.get(
                        "confidence",
                        0,
                    ),
                )
            )

            if probability <= 0:
                continue

            # --------------------------------------------------
            # EV
            # --------------------------------------------------

            ev = self.expected_value(
                probability,
                odd,
            )

            # --------------------------------------------------
            # VALUE BET
            # --------------------------------------------------

            is_value = (
                ev >= self.minimum_ev
            )

            opportunity = {

                "event_id":
                    event.get(
                        "event_id",
                        event.get(
                            "id",
                            "",
                        ),
                    ),

                "sport":
                    event.get(
                        "sport_title",
                        event.get(
                            "sport_key",
                            "",
                        ),
                    ),

                "home_team":
                    event.get(
                        "home_team",
                        "",
                    ),

                "away_team":
                    event.get(
                        "away_team",
                        "",
                    ),

                "market":
                    event.get(
                        "selected_market",
                        best_odd.get(
                            "market",
                            "",
                        ),
                    ),

                "selection":
                    event.get(
                        "selected_outcome",
                        best_odd.get(
                            "outcome",
                            "",
                        ),
                    ),

                "bookmaker":
                    event.get(
                        "selected_bookmaker",
                        best_odd.get(
                            "bookmaker",
                            "",
                        ),
                    ),

                "odd":
                    round(
                        odd,
                        3,
                    ),

                "probability":
                    round(
                        probability,
                        3,
                    ),

                "expected_value":
                    round(
                        ev,
                        3,
                    ),

                "oddreal_index":
                    event.get(
                        "oddreal_index",
                        0,
                    ),

                "confidence_level":
                    event.get(
                        "confidence_level",
                        "",
                    ),

                "average_odd":
                    event.get(
                        "average_odd",
                        0,
                    ),

                "market_variation":
                    event.get(
                        "market_variation",
                        0,
                    ),

                "risk":
                    event.get(
                        "risk",
                        "Alto",
                    ),

                "classification":
                    self.classify(
                        ev
                    ),

                "is_value_bet":
                    is_value,

            }

            opportunities.append(
                opportunity
            )

        info(
            f"{sum("
                1
                for item in opportunities
                if item.get("is_value_bet")
            )} Value Bets encontradas."
        )

        return opportunities

    # ==========================================================
    # MELHOR VALUE BET
    # ==========================================================

    def best_value_bet(
        self,
        opportunities: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not isinstance(
            opportunities,
            list,
        ):
            return None

        valid = [

            item

            for item in opportunities

            if isinstance(
                item,
                dict,
            )
        ]

        if not valid:
            return None

        value_bets = [

            item

            for item in valid

            if item.get(
                "is_value_bet",
                False,
            )
        ]

        if not value_bets:
            return None

        return max(
            value_bets,
            key=lambda item: (
                self._safe_float(
                    item.get(
                        "expected_value",
                        0,
                    )
                ),
                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0,
                    )
                ),
            ),
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "service":
                "ValueBetEngine",

            "minimum_ev":
                self.minimum_ev,

            "configured":
                True,

        }


# ==========================================================
# INSTÂNCIAS GLOBAIS
# ==========================================================

valuebet_engine = ValueBetEngine()

# Compatibilidade com versões anteriores
ValueEngine = ValueBetEngine

value_engine = valuebet_engine
