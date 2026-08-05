"""
OddReal 2.0
Motor Matemático de Value Bets

Arquivo:
oddsengine/value.py

Responsabilidades:
- Calcular probabilidades implícitas;
- Calcular overround/margem do mercado;
- Remover a margem do mercado;
- Calcular probabilidade justa de mercado;
- Identificar a melhor odd de uma seleção;
- Calcular EV usando probabilidade independente da odd avaliada;
- Identificar Value Bets;
- Classificar oportunidades;
- Selecionar a melhor Value Bet.

IMPORTANTE:
- Não consulta a API.
- Não utiliza IA.
- Não inventa probabilidade.
- Não utiliza a própria odd avaliada para criar uma falsa
  probabilidade de Value Bet.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info


class ValueBetEngine:
    """
    Motor matemático central do OddReal 2.0.

    A regra fundamental deste motor é:

        A probabilidade utilizada para calcular EV
        NÃO pode ser obtida da mesma odd que está
        sendo avaliada.

    Primeiro calculamos o consenso do mercado.
    Depois removemos a margem.
    Só então avaliamos o preço disponível.
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
        minimum_bookmakers: int = 2,
    ) -> None:

        self.minimum_ev = float(
            minimum_ev
        )

        self.minimum_bookmakers = int(
            minimum_bookmakers
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
        Conversão numérica segura.
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
        Probabilidade implícita de uma odd.

        Retorno em percentual.

        Exemplo:

            odd = 2.00
            resultado = 50.00
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return 100.0 / odd

    # ==========================================================
    # OVERROUND
    # ==========================================================

    def market_overround(
        self,
        probabilities: List[float],
    ) -> float:
        """
        Calcula a margem implícita do mercado.

        Exemplo:

            probabilidades = [52, 30, 23]

            soma = 105%

            overround = 5%
        """

        valid = [

            self._safe_float(
                value
            )

            for value in probabilities

            if self._safe_float(
                value
            ) > 0
        ]

        if not valid:
            return 0.0

        total = sum(valid)

        return round(
            total - 100.0,
            4,
        )

    # ==========================================================
    # PROBABILIDADES SEM MARGEM
    # ==========================================================

    def remove_margin(
        self,
        probabilities: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Remove proporcionalmente a margem do mercado.

        Exemplo:

            Fenerbahce = 65%
            Draw        = 22%
            Sturm       = 18%

            total = 105%

        As probabilidades são normalizadas para totalizar 100%.
        """

        if not isinstance(
            probabilities,
            dict,
        ):

            return {}

        valid = {

            key: self._safe_float(
                value
            )

            for key, value in probabilities.items()

            if self._safe_float(
                value
            ) > 0
        }

        if not valid:
            return {}

        total = sum(
            valid.values()
        )

        if total <= 0:
            return {}

        return {

            key: round(
                (
                    value
                    / total
                )
                * 100.0,
                4,
            )

            for key, value in valid.items()
        }

    # ==========================================================
    # PROBABILIDADE JUSTA DO MERCADO
    # ==========================================================

    def fair_market_probabilities(
        self,
        outcomes: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, float]:
        """
        Calcula probabilidades justas para um mercado.

        Cada item deve possuir:

            {
                "outcome": "Team A",
                "odd": 2.10
            }

        IMPORTANTE:

        Este método deve receber uma representação
        do mercado, preferencialmente baseada nas
        melhores odds disponíveis por seleção.

        A própria odd avaliada posteriormente NÃO deve
        ser utilizada isoladamente para calcular seu EV.
        """

        if not isinstance(
            outcomes,
            list,
        ):

            return {}

        implied: Dict[
            str,
            float
        ] = {}

        for item in outcomes:

            if not isinstance(
                item,
                dict,
            ):

                continue

            name = str(
                item.get(
                    "outcome",
                    "",
                )
            ).strip()

            odd = self._safe_float(
                item.get(
                    "odd",
                    0,
                )
            )

            if not name:
                continue

            if odd <= 1.0:
                continue

            probability = (
                self.implied_probability(
                    odd
                )
            )

            if probability <= 0:
                continue

            implied[name] = probability

        return self.remove_margin(
            implied
        )

    # ==========================================================
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> Optional[float]:
        """
        Calcula EV percentual.

        probability:
            percentual de 0 a 100.

        odd:
            preço que está sendo avaliado.

        Fórmula:

            EV = (P × odd) - 100

        IMPORTANTE:

        A probabilidade precisa ser independente
        da odd avaliada.

        Se probability for 11,76% e odd for 8,50:

            EV = 11,76 × 8,50 - 100
            ≈ 0%

        Isso é exatamente o comportamento que
        queremos evitar no cálculo de Value Bet.
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if (
            probability <= 0
            or odd <= 1.0
        ):

            return None

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
        probability: Optional[float],
        odd: float,
    ) -> bool:
        """
        Determina se uma oportunidade possui Value Bet.

        Se não houver probabilidade válida,
        NÃO existe Value Bet.
        """

        if probability is None:
            return False

        ev = self.expected_value(
            probability,
            odd,
        )

        if ev is None:
            return False

        return (
            ev >= self.minimum_ev
        )

    # ==========================================================
    # CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def classify(
        expected_value: Optional[float],
    ) -> str:
        """
        Classificação da oportunidade.
        """

        if expected_value is None:

            return "Indisponível"

        ev = float(
            expected_value
        )

        if ev >= 15.0:

            return "Excelente"

        if ev >= 10.0:

            return "Muito Forte"

        if ev >= 5.0:

            return "Value Bet"

        if ev > 0:

            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # EXTRAIR MERCADOS
    # ==========================================================

    def _extract_market_outcomes(
        self,
        event: Dict[str, Any],
        market_key: str,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Extrai os melhores preços disponíveis para cada
        seleção dentro de um mesmo mercado.

        Exemplo H2H:

            Fenerbahce
            Draw
            SK Sturm Graz

        Cada seleção recebe sua melhor odd disponível.

        Isso é fundamental para calcular a probabilidade
        justa do mercado.
        """

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            return []

        best_by_outcome: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            bookmaker_name = (
                bookmaker.get(
                    "title"
                )
                or bookmaker.get(
                    "key"
                )
                or "Desconhecida"
            )

            markets = bookmaker.get(
                "markets",
                [],
            )

            if not isinstance(
                markets,
                list,
            ):

                continue

            for market in markets:

                if not isinstance(
                    market,
                    dict,
                ):

                    continue

                current_market = str(
                    market.get(
                        "key",
                        "",
                    )
                ).strip()

                if (
                    current_market
                    != market_key
                ):

                    continue

                outcomes = market.get(
                    "outcomes",
                    [],
                )

                if not isinstance(
                    outcomes,
                    list,
                ):

                    continue

                for outcome in outcomes:

                    if not isinstance(
                        outcome,
                        dict,
                    ):

                        continue

                    name = str(
                        outcome.get(
                            "name",
                            "",
                        )
                    ).strip()

                    odd = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if (
                        not name
                        or odd <= 1.0
                    ):

                        continue

                    current = (
                        best_by_outcome.get(
                            name
                        )
                    )

                    if (
                        current is None
                        or odd
                        > self._safe_float(
                            current.get(
                                "odd",
                                0,
                            )
                        )
                    ):

                        best_by_outcome[
                            name
                        ] = {

                            "outcome":
                                name,

                            "odd":
                                odd,

                            "bookmaker":
                                bookmaker_name,

                            "market":
                                market_key,

                        }

        return list(
            best_by_outcome.values()
        )

    # ==========================================================
    # ANALISAR EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Analisa um evento completo.

        O cálculo é feito por mercado.

        Neste estágio o motor utiliza o consenso
        de mercado para produzir a probabilidade justa.

        A melhor odd é então comparada contra essa
        probabilidade.
        """

        if not isinstance(
            event,
            dict,
        ):

            return None

        market = str(
            event.get(
                "selected_market",
                "h2h",
            )
        ).strip()

        if not market:

            market = "h2h"

        market_outcomes = (
            self._extract_market_outcomes(
                event,
                market,
            )
        )

        if not market_outcomes:

            return None

        # ------------------------------------------------------
        # PROBABILIDADE JUSTA
        # ------------------------------------------------------

        fair_probabilities = (
            self.fair_market_probabilities(
                market_outcomes
            )
        )

        if not fair_probabilities:

            return None

        # ------------------------------------------------------
        # SELEÇÃO
        # ------------------------------------------------------

        selected_outcome = str(
            event.get(
                "selected_outcome",
                "",
            )
        ).strip()

        if not selected_outcome:

            return None

        probability = fair_probabilities.get(
            selected_outcome
        )

        if probability is None:

            return None

        # ------------------------------------------------------
        # MELHOR ODD DA SELEÇÃO
        # ------------------------------------------------------

        selected_price = None

        selected_bookmaker = ""

        for item in market_outcomes:

            if (
                item.get(
                    "outcome",
                    "",
                )
                == selected_outcome
            ):

                selected_price = (
                    self._safe_float(
                        item.get(
                            "odd",
                            0,
                        )
                    )
                )

                selected_bookmaker = (
                    item.get(
                        "bookmaker",
                        "",
                    )
                )

                break

        if (
            selected_price is None
            or selected_price <= 1.0
        ):

            return None

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        ev = self.expected_value(
            probability,
            selected_price,
        )

        if ev is None:

            return None

        return {

            "event_id":
                event.get(
                    "id",
                    "",
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
                market,

            "selection":
                selected_outcome,

            "bookmaker":
                selected_bookmaker,

            "odd":
                round(
                    selected_price,
                    3,
                ),

            "probability":
                round(
                    probability,
                    4,
                ),

            "expected_value":
                round(
                    ev,
                    4,
                ),

            "overround":
                round(
                    self.market_overround(
                        [
                            self.implied_probability(
                                item.get(
                                    "odd",
                                    0,
                                )
                            )

                            for item
                            in market_outcomes
                        ]
                    ),
                    4,
                ),

            "classification":
                self.classify(
                    ev
                ),

            "is_value_bet":
                self.is_value_bet(
                    probability,
                    selected_price,
                ),

            "market_probabilities":
                fair_probabilities,

        }

    # ==========================================================
    # ANALISAR LISTA
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
        Analisa os eventos recebidos pelo Analyzer.

        Observação:

        Este método preserva a estrutura esperada
        pelo restante do OddReal.
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

                result = (
                    self.analyze_event(
                        event
                    )
                )

                if result is not None:

                    opportunities.append(
                        result
                    )

            except Exception:

                continue

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
        Retorna a oportunidade com maior EV.
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
            and item.get(
                "is_value_bet",
                False,
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
                        "probability",
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
        Estado atual do motor.
        """

        return {

            "service":
                "ValueBetEngine",

            "minimum_ev":
                self.minimum_ev,

            "minimum_bookmakers":
                self.minimum_bookmakers,

            "method":
                "market_consensus_without_margin",

            "configured":
                True,

        }


# ==========================================================
# COMPATIBILIDADE
# ==========================================================

# A versão antiga do projeto utilizava ValueEngine.
# Mantemos um alias para evitar quebra de imports antigos.

ValueEngine = ValueBetEngine


# ==========================================================
# INSTÂNCIA GLOBAL PRINCIPAL
# ==========================================================

valuebet_engine = ValueBetEngine()


# ==========================================================
# ALIAS DE COMPATIBILIDADE
# ==========================================================

value_engine = valuebet_engine
