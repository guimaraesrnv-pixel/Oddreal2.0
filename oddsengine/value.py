"""
OddReal 2.0
Motor de Value Bets

Arquivo:
oddsengine/value.py

Responsável por:
- Probabilidade implícita;
- Probabilidade justa de mercado;
- Remoção aproximada da margem (vig/overround);
- Valor esperado (EV);
- Identificação de Value Bets;
- Classificação das oportunidades;
- Seleção da melhor Value Bet.

IMPORTANTE:
- Não consulta a API.
- Não utiliza IA.
- Não escolhe bookmakers.
- Trabalha somente com dados recebidos do Analyzer.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error


class ValueBetEngine:
    """
    Motor matemático de Value Bets do OddReal 2.0.

    A principal diferença desta versão é que a probabilidade
    usada no EV NÃO vem da própria odd avaliada.

    A probabilidade é estimada a partir do consenso das odds
    disponíveis para o mesmo mercado e seleção.
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
    ) -> None:

        self.minimum_ev = float(minimum_ev)

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
        Converte uma odd decimal em probabilidade implícita.

        Exemplo:

        2.00 -> 50%
        4.00 -> 25%
        5.00 -> 20%
        """

        odd = self._safe_float(odd)

        if odd <= 0:
            return 0.0

        return 100.0 / odd

    # ==========================================================
    # PROBABILIDADE JUSTA
    # ==========================================================

    def fair_probability_from_market(
        self,
        outcome_odds: List[float],
    ) -> float:
        """
        Estima a probabilidade justa de cada resultado
        removendo aproximadamente a margem do mercado.

        Exemplo:

        Casa A:
            Vitória = 2.00
            Empate  = 3.50
            Derrota = 4.00

        Primeiro calculamos as probabilidades implícitas:

            50.00%
            28.57%
            25.00%

        Soma:

            103.57%

        A margem aproximada é removida normalizando
        as probabilidades.

        IMPORTANTE:
        Esta função recebe as odds de TODOS os resultados
        do mesmo mercado, e não apenas a odd avaliada.
        """

        if not isinstance(
            outcome_odds,
            list,
        ):

            return 0.0

        probabilities: List[float] = []

        for odd in outcome_odds:

            price = self._safe_float(odd)

            if price <= 0:
                continue

            probability = (
                self.implied_probability(price)
            )

            if probability > 0:
                probabilities.append(
                    probability
                )

        if not probabilities:
            return 0.0

        total = sum(probabilities)

        if total <= 0:
            return 0.0

        return 0.0

    # ==========================================================
    # PROBABILIDADE JUSTA DE UM RESULTADO
    # ==========================================================

    def normalized_probability(
        self,
        target_odd: float,
        market_odds: List[float],
    ) -> float:
        """
        Calcula a probabilidade justa aproximada de uma
        seleção utilizando todas as seleções do mesmo mercado.

        A margem do mercado é retirada por normalização.

        Retorno em escala 0-100.
        """

        target_odd = self._safe_float(
            target_odd
        )

        if target_odd <= 0:
            return 0.0

        if not isinstance(
            market_odds,
            list,
        ):

            return 0.0

        probabilities: List[float] = []

        for odd in market_odds:

            price = self._safe_float(
                odd
            )

            if price <= 0:
                continue

            probabilities.append(
                self.implied_probability(
                    price
                )
            )

        if not probabilities:
            return 0.0

        total_probability = sum(
            probabilities
        )

        if total_probability <= 0:
            return 0.0

        target_probability = (
            self.implied_probability(
                target_odd
            )
        )

        fair_probability = (
            target_probability
            / total_probability
        ) * 100.0

        return round(
            fair_probability,
            4,
        )

    # ==========================================================
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o valor esperado percentual.

        probability:
            probabilidade em escala 0-100.

        Fórmula:

            EV = ((p / 100) × odd - 1) × 100

        Exemplo:

            Probabilidade = 25%
            Odd = 5.00

            EV = ((0.25 × 5) - 1) × 100
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
                    probability / 100.0
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
    ) -> bool:
        """
        Verifica se o EV atingiu o limite mínimo.
        """

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
        """
        Classifica a força matemática da oportunidade.
        """

        ev = float(
            expected_value
        )

        if ev >= 20:
            return "Excelente"

        if ev >= 15:
            return "Muito Forte"

        if ev >= 10:
            return "Forte"

        if ev >= 5:
            return "Value Bet"

        if ev > 0:
            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # ANALISAR VALUE BETS
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
        Identifica Value Bets a partir das análises
        matematicamente calculadas.

        O campo 'expected_value' já deve ter sido calculado
        pelo Analyzer usando uma probabilidade que não seja
        a própria probabilidade implícita da odd avaliada.
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

            odd = self._safe_float(
                event.get(
                    "odd",
                    0,
                )
            )

            if odd <= 0:
                continue

            probability = self._safe_float(
                event.get(
                    "probability",
                    0,
                )
            )

            if probability <= 0:
                continue

            ev = self._safe_float(
                event.get(
                    "expected_value",
                    0,
                )
            )

            if ev < self.minimum_ev:
                continue

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
                        "",
                    ),

                "selection":
                    event.get(
                        "selected_outcome",
                        "",
                    ),

                "bookmaker":
                    event.get(
                        "selected_bookmaker",
                        "",
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

            }

            opportunities.append(
                opportunity
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
        Seleciona a melhor Value Bet.

        Prioridade:

        1. Maior EV;
        2. Maior Índice OddReal.
        """

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

valuebet_engine = ValueBetEngine()


# ==========================================================
# COMPATIBILIDADE COM MÓDULOS LEGADOS
# ==========================================================

ValueEngine = ValueBetEngine
