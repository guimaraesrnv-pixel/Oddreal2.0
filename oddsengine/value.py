"""
OddReal 2.0
Motor de Value Bets

Arquivo:
oddsengine/value.py

Responsável por:
- Probabilidade implícita;
- Probabilidade de consenso do mercado;
- Valor esperado (EV);
- Identificação de Value Bets;
- Classificação das oportunidades;
- Seleção da melhor Value Bet.

Não consulta API.
Não utiliza IA.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error


class ValueBetEngine:
    """
    Motor responsável exclusivamente pela análise
    matemática de Value Bets.
    """

    def __init__(
        self,
        minimum_ev: float = 1.0,
    ) -> None:

        self.minimum_ev = max(
            0.0,
            float(minimum_ev),
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
        """
        Converte valores numéricos com segurança.
        """

        try:

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
        """
        Calcula a probabilidade implícita de uma odd.

        Exemplo:

        Odd 2.00
        -> 50%

        Odd 4.00
        -> 25%
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 0:

            return 0.0

        return 100.0 / odd

    # ==========================================================
    # PROBABILIDADE DE CONSENSO
    # ==========================================================

    def market_probability(
        self,
        average_odd: float,
    ) -> float:
        """
        Calcula a probabilidade implícita baseada
        na odd média do mercado.

        Essa é a principal referência utilizada
        pelo motor para estimar o consenso.

        Exemplo:

        Odd média = 4.00

        Probabilidade de consenso = 25%
        """

        average_odd = self._safe_float(
            average_odd
        )

        if average_odd <= 0:

            return 0.0

        return (
            100.0 / average_odd
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
        Calcula o valor esperado percentual.

        probability deve estar em escala 0-100.

        Fórmula:

            EV = ((probabilidade / 100) * odd - 1) * 100

        Exemplo:

            Probabilidade = 25%
            Odd = 5.00

            EV = 25%
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if (
            probability <= 0
            or odd <= 0
        ):

            return 0.0

        return round(
            (
                (
                    probability
                    / 100.0
                )
                * odd
                - 1.0
            )
            * 100.0,
            4,
        )

    # ==========================================================
    # VALUE BET
    # ==========================================================

    def is_value_bet(
        self,
        probability: float,
        odd: float,
        minimum_ev: Optional[
            float
        ] = None,
    ) -> bool:
        """
        Verifica se uma oportunidade
        possui EV suficiente.

        EV negativo nunca é Value Bet.

        Por padrão utiliza self.minimum_ev.
        """

        ev = self.expected_value(
            probability,
            odd,
        )

        threshold = (
            self.minimum_ev
            if minimum_ev is None
            else max(
                0.0,
                self._safe_float(
                    minimum_ev
                ),
            )
        )

        return (
            ev >= threshold
        )

    # ==========================================================
    # CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def classify(
        expected_value: float,
    ) -> str:
        """
        Classifica a força matemática
        da oportunidade.
        """

        ev = ValueBetEngine._safe_float(
            expected_value
        )

        if ev >= 20:

            return "Excepcional"

        if ev >= 15:

            return "Excelente"

        if ev >= 10:

            return "Muito Forte"

        if ev >= 5:

            return "Value Bet Forte"

        if ev > 0:

            return "Value Bet"

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
        """
        Analisa as oportunidades recebidas
        pelo Analyzer.

        IMPORTANTE:

        O EV NÃO deve ser calculado utilizando
        a probabilidade implícita da própria odd.

        Isso produziria aproximadamente:

            (1 / odd) * odd - 1 = 0

        Portanto, quando disponível, utilizamos
        a odd média do mercado para obter uma
        probabilidade de consenso.

        Exemplo:

            Odd selecionada = 5.20
            Odd média = 4.80

            Probabilidade consenso =
            100 / 4.80 = 20.83%

            EV =
            ((20.83 / 100) * 5.20 - 1) * 100

            EV ≈ 8.33%
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

                # ==================================================
                # ODD
                # ==================================================

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

                # ==================================================
                # ODD MÉDIA DO MERCADO
                # ==================================================

                average_odd = self._safe_float(
                    event.get(
                        "average_odd",
                        0,
                    )
                )

                # ==================================================
                # PROBABILIDADE
                # ==================================================
                #
                # Prioridade:
                #
                # 1. market_probability
                # 2. probability_model
                # 3. probability
                # 4. confidence
                # 5. odd média
                #
                # Porém, para Value Bet, a odd média
                # continua sendo a referência principal
                # quando disponível.
                #

                if average_odd > 0:

                    probability = (
                        self.market_probability(
                            average_odd
                        )
                    )

                else:

                    probability = self._safe_float(
                        event.get(
                            "market_probability",
                            event.get(
                                "probability_model",
                                event.get(
                                    "probability",
                                    event.get(
                                        "confidence",
                                        0,
                                    ),
                                ),
                            ),
                        )
                    )

                if probability <= 0:

                    continue

                # ==================================================
                # EV
                # ==================================================

                ev = self.expected_value(
                    probability,
                    odd,
                )

                # ==================================================
                # VALUE BET
                # ==================================================

                is_value = self.is_value_bet(
                    probability,
                    odd,
                )

                # ==================================================
                # VARIAÇÃO
                # ==================================================

                market_variation = self._safe_float(
                    event.get(
                        "market_variation",
                        0,
                    )
                )

                # ==================================================
                # ÍNDICE ODREAL
                # ==================================================

                oddreal_index = self._safe_float(
                    event.get(
                        "oddreal_index",
                        0,
                    )
                )

                # ==================================================
                # CLASSIFICAÇÃO
                # ==================================================

                classification = self.classify(
                    ev
                )

                # ==================================================
                # OBJETO DE OPORTUNIDADE
                # ==================================================

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

                    "market_probability":
                        round(
                            probability,
                            3,
                        ),

                    "implied_probability":
                        round(
                            self.implied_probability(
                                odd
                            ),
                            3,
                        ),

                    "expected_value":
                        round(
                            ev,
                            3,
                        ),

                    "oddreal_index":
                        int(
                            round(
                                oddreal_index
                            )
                        ),

                    "confidence_level":
                        event.get(
                            "confidence_level",
                            "",
                        ),

                    "average_odd":
                        round(
                            average_odd,
                            3,
                        ),

                    "market_variation":
                        round(
                            market_variation,
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
                        is_value,

                }

                # ==================================================
                # FILTRO FINAL
                # ==================================================
                #
                # Somente oportunidades realmente
                # qualificadas entram na lista.
                #
                # EV negativo:
                # NÃO entra.
                #
                # EV positivo abaixo do limite:
                # NÃO entra.
                #

                if is_value:

                    opportunities.append(
                        opportunity
                    )

            except Exception as exc:

                error(
                    "Erro ao analisar "
                    f"Value Bet: {exc}"
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

        Critério principal:
        maior EV.

        Critério de desempate:
        maior Índice OddReal.
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
                        0,
                    )
                ) >= self.minimum_ev
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
        """
        Retorna o estado do motor.
        """

        return {

            "service":
                "ValueBetEngine",

            "minimum_ev":
                self.minimum_ev,

            "configured":
                True,

        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

valuebet_engine = ValueBetEngine(
    minimum_ev=1.0
)
