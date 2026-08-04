"""
OddReal 2.0
Motor de Value Bets

Responsável exclusivamente por identificar oportunidades
de Value Bet a partir dos indicadores calculados pelo
Analyzer/OddsEngine.

A chave da API não é utilizada neste módulo.
"""

from __future__ import annotations

from typing import Any, Dict, List

from modules.logger import info, error


class ValueBetEngine:
    """
    Motor central de identificação de Value Bets.

    Regra:
        EV = (probabilidade × odd) - 100

    A probabilidade recebida deve estar em percentual.
    Exemplo:
        probability = 55
        odd = 2.10

    EV = (55 × 2.10) - 100
       = 15.50%
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
    ) -> None:

        self.minimum_ev = float(
            minimum_ev
        )

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    @staticmethod
    def implied_probability(
        odd: float,
    ) -> float:
        """
        Calcula a probabilidade implícita da odd.

        Retorno em percentual.
        """

        try:

            odd = float(odd)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if odd <= 0:

            return 0.0

        return round(
            100.0 / odd,
            4,
        )

    # ==========================================================
    # EXPECTED VALUE
    # ==========================================================

    @staticmethod
    def expected_value(
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o Valor Esperado percentual.

        probability:
            percentual entre 0 e 100.

        odd:
            odd decimal.
        """

        try:

            probability = float(
                probability
            )

            odd = float(
                odd
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if (
            probability <= 0
            or odd <= 0
        ):

            return 0.0

        return round(
            (
                probability * odd
            ) - 100.0,
            4,
        )

    # ==========================================================
    # VERIFICAR VALUE BET
    # ==========================================================

    def is_value_bet(
        self,
        probability: float,
        odd: float,
    ) -> bool:
        """
        Determina se a oportunidade ultrapassa
        o EV mínimo configurado.
        """

        ev = self.expected_value(
            probability,
            odd,
        )

        return (
            ev >= self.minimum_ev
        )

    # ==========================================================
    # ANALISAR OPORTUNIDADES
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
        Identifica Value Bets usando os indicadores
        já calculados pelo Analyzer.

        IMPORTANTE:
        Não utiliza confidence como probabilidade.

        A probabilidade deve vir do campo:
            probability

        Isso evita misturar confiança do modelo
        com probabilidade matemática.
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

            try:

                # --------------------------------------------------
                # IDENTIDADE DO EVENTO
                # --------------------------------------------------

                event_id = event.get(
                    "event_id",
                    event.get(
                        "id",
                        "",
                    ),
                )

                home_team = event.get(
                    "home_team",
                    "",
                )

                away_team = event.get(
                    "away_team",
                    "",
                )

                # --------------------------------------------------
                # ODD
                # --------------------------------------------------

                best_odd = event.get(
                    "best_odd",
                    {},
                )

                if isinstance(
                    best_odd,
                    dict,
                ):

                    odd = best_odd.get(
                        "odd",
                        event.get(
                            "odd",
                            0,
                        ),
                    )

                    bookmaker = (
                        best_odd.get(
                            "bookmaker",
                            "",
                        )
                    )

                    market = (
                        best_odd.get(
                            "market",
                            "",
                        )
                    )

                    outcome = (
                        best_odd.get(
                            "outcome",
                            "",
                        )
                    )

                else:

                    odd = event.get(
                        "odd",
                        0,
                    )

                    bookmaker = event.get(
                        "selected_bookmaker",
                        "",
                    )

                    market = event.get(
                        "selected_market",
                        "",
                    )

                    outcome = event.get(
                        "selected_outcome",
                        "",
                    )

                # --------------------------------------------------
                # PROBABILIDADE
                # --------------------------------------------------

                probability = event.get(
                    "probability",
                    0,
                )

                # --------------------------------------------------
                # VALIDAÇÃO
                # --------------------------------------------------

                try:

                    odd = float(
                        odd
                    )

                    probability = float(
                        probability
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

                if (
                    odd <= 0
                    or probability <= 0
                ):

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

                if ev < self.minimum_ev:

                    continue

                opportunity = {

                    "event_id":
                        event_id,

                    "home_team":
                        home_team,

                    "away_team":
                        away_team,

                    "market":
                        market,

                    "selection":
                        outcome,

                    "outcome":
                        outcome,

                    "bookmaker":
                        bookmaker,

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

                    "implied_probability":
                        self.implied_probability(
                            odd
                        ),

                    "expected_value":
                        ev,

                    "minimum_ev":
                        self.minimum_ev,

                    "is_value_bet":
                        True,

                }

                opportunities.append(
                    opportunity
                )

            except Exception as exc:

                error(
                    "Erro ao analisar "
                    f"Value Bet: {exc}"
                )

        # ------------------------------------------------------
        # ORDENAÇÃO
        # ------------------------------------------------------

        opportunities.sort(
            key=lambda item: item.get(
                "expected_value",
                0,
            ),
            reverse=True,
        )

        info(
            f"{len(opportunities)} "
            "Value Bets encontradas."
        )

        return opportunities


# ==============================================================
# INSTÂNCIA GLOBAL
# ==============================================================

valuebet_engine = ValueBetEngine()
