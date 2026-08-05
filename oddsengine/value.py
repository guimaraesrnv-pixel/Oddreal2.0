"""
OddReal 2.0
Motor de Value Bets

Responsável por:

- probabilidade implícita;
- valor esperado (EV);
- identificação de Value Bets;
- classificação matemática;
- seleção da melhor Value Bet;
- compatibilidade com versões anteriores.

Este módulo NÃO consulta API.
Este módulo NÃO utiliza IA.
Este módulo NÃO altera bookmakers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info


class ValueBetEngine:
    """
    Motor matemático de Value Bets.

    A probabilidade usada no EV deve ser uma
    probabilidade estimada independente da odd
    específica que está sendo avaliada.

    probability:
        probabilidade estimada em percentual.
        Exemplo: 15.0 = 15%.

    odd:
        odd decimal.
        Exemplo: 8.00.
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
    # UTILITÁRIO
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Conversão segura para float.
        """

        try:

            if value is None:
                return default

            result = float(value)

            if result != result:
                return default

            if result in (
                float("inf"),
                float("-inf"),
            ):
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
        """
        Probabilidade implícita da odd.

        P = 1 / odd

        Retorno em percentual.
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return round(
            (1.0 / odd) * 100.0,
            4,
        )

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

        EV = ((P / 100) × odd - 1) × 100

        Exemplo:

        P = 15%
        odd = 8.00

        EV = ((0.15 × 8) - 1) × 100
           = 20%
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if probability <= 0:
            return 0.0

        if odd <= 1.0:
            return 0.0

        probability = min(
            probability,
            100.0,
        )

        probability_decimal = (
            probability / 100.0
        )

        ev = (
            probability_decimal
            * odd
            - 1.0
        ) * 100.0

        return round(
            ev,
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
        """
        Uma seleção somente é Value Bet quando:

            EV >= minimum_ev

        Padrão:

            EV >= 5%
        """

        ev = self.expected_value(
            probability,
            odd,
        )

        return (
            ev >= self.minimum_ev
        )

    # ==========================================================
    # CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def classify(
        expected_value: float,
    ) -> str:
        """
        Classifica a força do EV.
        """

        ev = ValueBetEngine._safe_float(
            expected_value
        )

        if ev >= 20.0:
            return "Excelente"

        if ev >= 15.0:
            return "Muito Forte"

        if ev >= 10.0:
            return "Forte"

        if ev >= 5.0:
            return "Value Bet"

        if ev > 0.0:
            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # NORMALIZAÇÃO DA ODD
    # ==========================================================

    @staticmethod
    def _extract_odd(
        value: Any,
    ) -> float:
        """
        Aceita:

            odd = 8.50

        ou:

            {
                "odd": 8.50
            }

        para manter compatibilidade com versões antigas.
        """

        if isinstance(
            value,
            dict,
        ):

            return ValueBetEngine._safe_float(
                value.get(
                    "odd",
                    0.0,
                )
            )

        return ValueBetEngine._safe_float(
            value
        )

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
        """
        Recebe análises já produzidas pelo Analyzer.

        Recalcula:

        - odd;
        - probabilidade;
        - EV;
        - classificação;
        - flag de Value Bet.

        Retorna SOMENTE Value Bets.
        """

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

            odd = self._extract_odd(
                event.get(
                    "odd",
                    event.get(
                        "best_odd",
                        0.0,
                    ),
                )
            )

            if odd <= 1.0:
                continue

            # --------------------------------------------------
            # PROBABILIDADE
            # --------------------------------------------------

            probability = self._safe_float(
                event.get(
                    "probability",
                    0.0,
                )
            )

            if probability <= 0.0:

                # Compatibilidade antiga.
                probability = self._safe_float(
                    event.get(
                        "market_probability",
                        0.0,
                    )
                )

            if probability <= 0.0:
                continue

            probability = min(
                probability,
                100.0,
            )

            # --------------------------------------------------
            # PROBABILIDADE IMPLÍCITA
            # --------------------------------------------------

            implied_probability = (
                self.implied_probability(
                    odd
                )
            )

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

            if not is_value:
                continue

            # --------------------------------------------------
            # CLASSIFICAÇÃO
            # --------------------------------------------------

            classification = (
                self.classify(
                    ev
                )
            )

            # --------------------------------------------------
            # RESULTADO
            # --------------------------------------------------

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
                        "sport",
                        event.get(
                            "sport_title",
                            event.get(
                                "sport_key",
                                "",
                            ),
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
                        "market",
                        event.get(
                            "selected_market",
                            "",
                        ),
                    ),

                "selection":
                    event.get(
                        "selection",
                        event.get(
                            "outcome",
                            event.get(
                                "selected_outcome",
                                "",
                            ),
                        ),
                    ),

                "bookmaker":
                    event.get(
                        "bookmaker",
                        event.get(
                            "selected_bookmaker",
                            "",
                        ),
                    ),

                "odd":
                    round(
                        odd,
                        3,
                    ),

                "best_odd":
                    round(
                        odd,
                        3,
                    ),

                "probability":
                    round(
                        probability,
                        3,
                    ),

                "market_probability":
                    round(
                        probability,
                        3,
                    ),

                "implied_probability":
                    round(
                        implied_probability,
                        3,
                    ),

                "expected_value":
                    round(
                        ev,
                        3,
                    ),

                "oddreal_index":
                    round(
                        self._safe_float(
                            event.get(
                                "oddreal_index",
                                0.0,
                            )
                        ),
                        2,
                    ),

                "confidence_level":
                    event.get(
                        "confidence_level",
                        event.get(
                            "confidence",
                            "",
                        ),
                    ),

                "confidence":
                    event.get(
                        "confidence",
                        event.get(
                            "confidence_level",
                            "",
                        ),
                    ),

                "average_odd":
                    round(
                        self._safe_float(
                            event.get(
                                "average_odd",
                                0.0,
                            )
                        ),
                        3,
                    ),

                "market_variation":
                    round(
                        self._safe_float(
                            event.get(
                                "market_variation",
                                0.0,
                            )
                        ),
                        3,
                    ),

                "risk":
                    event.get(
                        "risk",
                        "Alto",
                    ),

                "classification":
                    classification,

                "is_value_bet":
                    True,
            }

            opportunities.append(
                opportunity
            )

        opportunities.sort(
            key=lambda item: (
                self._safe_float(
                    item.get(
                        "expected_value",
                        0.0,
                    )
                ),
                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0.0,
                    )
                ),
            ),
            reverse=True,
        )

        info(
            f"{len(opportunities)} "
            "Value Bets encontradas."
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
        """
        Retorna a melhor Value Bet.

        Prioridade:

        1. maior EV;
        2. maior Índice OddReal;
        3. maior probabilidade.
        """

        if not isinstance(
            opportunities,
            list,
        ):
            return None

        valid = [

            item

            for item in opportunities

            if (
                isinstance(
                    item,
                    dict,
                )
                and self._safe_float(
                    item.get(
                        "expected_value",
                        0.0,
                    )
                )
                >= self.minimum_ev
            )
        ]

        if not valid:
            return None

        return max(
            valid,
            key=lambda item: (
                self._safe_float(
                    item.get(
                        "expected_value",
                        0.0,
                    )
                ),
                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0.0,
                    )
                ),
                self._safe_float(
                    item.get(
                        "probability",
                        0.0,
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
# COMPATIBILIDADE
# ==========================================================

ValueEngine = ValueBetEngine


# ==========================================================
# INSTÂNCIAS GLOBAIS
# ==========================================================

valuebet_engine = ValueBetEngine()

value_engine = valuebet_engine


__all__ = [
    "ValueBetEngine",
    "ValueEngine",
    "valuebet_engine",
    "value_engine",
]
