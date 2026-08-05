"""
OddReal 2.0
Analyzer

Arquivo:
core/analyzer.py

Responsável por:
- Analisar eventos preparados pelo Pipeline;
- Selecionar a melhor odd;
- Calcular indicadores básicos;
- Calcular probabilidade de mercado;
- Calcular EV real em relação ao consenso;
- Integrar o ValueBetEngine;
- Identificar Value Bets;
- Encontrar melhores oportunidades;
- Gerar resumo das análises.

IMPORTANTE:
- Não consulta diretamente a The Odds API.
- Não contém API Key.
- Não utiliza IA para cálculos.
- A IA permanece na camada interpretativa.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error
from oddsengine.value import valuebet_engine


class Analyzer:
    """
    Camada central de análise do OddReal 2.0.
    """

    def __init__(self) -> None:

        info(
            "Analyzer OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
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

    @staticmethod
    def _normalize_probability(
        value: float,
    ) -> float:
        """
        Normaliza uma probabilidade para percentual
        entre 0 e 100.

        O sistema trabalha internamente com percentual.
        """

        value = Analyzer._safe_float(
            value
        )

        if value <= 0:
            return 0.0

        # Caso venha como decimal:
        # 0.35 -> 35%
        if value <= 1.0:

            value *= 100.0

        return min(
            max(
                value,
                0.0,
            ),
            100.0,
        )

    # ==========================================================
    # MELHOR ODD
    # ==========================================================

    def _get_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna a maior odd disponível no evento.

        Se o Pipeline já tiver produzido best_odd,
        utiliza essa informação.
        """

        existing = event.get(
            "best_odd"
        )

        if isinstance(
            existing,
            dict,
        ):

            odd = self._safe_float(
                existing.get(
                    "odd",
                    existing.get(
                        "price",
                        0,
                    ),
                )
            )

            if odd > 0:

                return {
                    "odd": odd,
                    "bookmaker": existing.get(
                        "bookmaker",
                        existing.get(
                            "title",
                            existing.get(
                                "name",
                                "",
                            ),
                        ),
                    ),
                    "market": existing.get(
                        "market",
                        existing.get(
                            "key",
                            "",
                        ),
                    ),
                    "outcome": existing.get(
                        "outcome",
                        existing.get(
                            "name",
                            "",
                        ),
                    ),
                }

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            return None

        best: Optional[
            Dict[str, Any]
        ] = None

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            bookmaker_name = (
                bookmaker.get(
                    "title",
                    bookmaker.get(
                        "name",
                        bookmaker.get(
                            "key",
                            "",
                        ),
                    ),
                )
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

                market_name = market.get(
                    "key",
                    "",
                )

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

                    odd = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if odd <= 0:
                        continue

                    candidate = {
                        "odd": odd,
                        "bookmaker": bookmaker_name,
                        "market": market_name,
                        "outcome": outcome.get(
                            "name",
                            "",
                        ),
                    }

                    if (
                        best is None
                        or odd > self._safe_float(
                            best.get(
                                "odd",
                                0,
                            )
                        )
                    ):

                        best = candidate

        return best

    # ==========================================================
    # ODDS DO MERCADO
    # ==========================================================

    def _collect_market_odds(
        self,
        event: Dict[str, Any],
        selected_market: str,
    ) -> Dict[str, List[float]]:
        """
        Coleta as odds de todas as casas para cada seleção
        dentro do mesmo mercado.

        Exemplo:

        Home:
            [2.10, 2.05, 2.15]

        Draw:
            [3.20, 3.30, 3.25]

        Away:
            [3.50, 3.60, 3.55]

        Isso permite calcular uma probabilidade de mercado
        independente da melhor odd escolhida.
        """

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):
            return {}

        market_odds: Dict[
            str,
            List[float]
        ] = {}

        selected_market = str(
            selected_market or ""
        ).strip()

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

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

                market_key = str(
                    market.get(
                        "key",
                        "",
                    )
                ).strip()

                if (
                    selected_market
                    and market_key
                    != selected_market
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

                    outcome_name = str(
                        outcome.get(
                            "name",
                            "",
                        )
                    ).strip()

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if (
                        not outcome_name
                        or price <= 0
                    ):
                        continue

                    if outcome_name not in market_odds:

                        market_odds[
                            outcome_name
                        ] = []

                    market_odds[
                        outcome_name
                    ].append(
                        price
                    )

        return market_odds

    # ==========================================================
    # MÉDIA DE MERCADO
    # ==========================================================

    def _calculate_market_average(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
        selected_market: str = "",
    ) -> float:
        """
        Calcula a média das odds para a mesma seleção
        dentro do mesmo mercado.
        """

        market_odds = (
            self._collect_market_odds(
                event,
                selected_market,
            )
        )

        prices = market_odds.get(
            selected_outcome,
            [],
        )

        if not prices:
            return 0.0

        return round(
            sum(prices)
            / len(prices),
            4,
        )

    # ==========================================================
    # PROBABILIDADE DE MERCADO
    # ==========================================================

    def _calculate_market_probability(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
        selected_market: str,
        selected_odd: float,
    ) -> float:
        """
        Calcula uma probabilidade estimada pelo consenso
        do mercado.

        IMPORTANTE:

        A probabilidade NÃO é calculada usando a própria
        melhor odd.

        Primeiro são calculadas as odds médias de cada
        seleção do mercado.

        Depois:

            probabilidade bruta = 1 / odd média

        Como as probabilidades implícitas podem carregar
        margem da casa, elas são normalizadas para que a
        soma seja aproximadamente 100%.

        Isso cria uma estimativa de consenso de mercado
        independente da melhor odd disponível.
        """

        market_odds = (
            self._collect_market_odds(
                event,
                selected_market,
            )
        )

        if not market_odds:

            # Fallback somente quando não conseguimos
            # encontrar estrutura suficiente no mercado.

            if selected_odd > 0:

                return round(
                    (
                        1.0
                        / selected_odd
                    )
                    * 100.0,
                    4,
                )

            return 0.0

        average_odds: Dict[
            str,
            float
        ] = {}

        for outcome_name, prices in market_odds.items():

            valid_prices = [

                self._safe_float(
                    price
                )

                for price in prices

                if self._safe_float(
                    price
                ) > 0
            ]

            if not valid_prices:
                continue

            average_odds[
                outcome_name
            ] = (
                sum(valid_prices)
                / len(valid_prices)
            )

        if not average_odds:
            return 0.0

        implied_probabilities: Dict[
            str,
            float
        ] = {}

        for outcome_name, average_odd in average_odds.items():

            if average_odd <= 0:
                continue

            implied_probabilities[
                outcome_name
            ] = 1.0 / average_odd

        total_probability = sum(
            implied_probabilities.values()
        )

        if total_probability <= 0:
            return 0.0

        selected_probability = (
            implied_probabilities.get(
                selected_outcome,
                0.0,
            )
        )

        if selected_probability <= 0:
            return 0.0

        normalized_probability = (
            selected_probability
            / total_probability
        )

        return round(
            normalized_probability
            * 100.0,
            4,
        )

    # ==========================================================
    # VARIAÇÃO DO MERCADO
    # ==========================================================

    @staticmethod
    def _market_variation(
        odd: float,
        average_odd: float,
    ) -> float:
        """
        Calcula quanto a melhor odd está acima/abaixo
        da média do mercado.

        Retorno em percentual.
        """

        if average_odd <= 0:
            return 0.0

        return round(
            (
                (
                    odd
                    - average_odd
                )
                / average_odd
            )
            * 100.0,
            4,
        )

    # ==========================================================
    # NÍVEL DE RISCO
    # ==========================================================

    @staticmethod
    def _risk_level(
        probability: float,
        expected_value: float,
        variation: float,
    ) -> str:
        """
        Classificação simples de risco.

        Não representa garantia de resultado.
        """

        if (
            probability >= 70
            and expected_value >= 10
            and variation >= 0
        ):
            return "Baixo"

        if (
            probability >= 55
            and expected_value > 0
        ):
            return "Moderado"

        return "Alto"

    # ==========================================================
    # ANÁLISE DE UM EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Analisa um evento individual.
        """

        if not isinstance(
            event,
            dict,
        ):
            return None

        best_odd = self._get_best_odd(
            event
        )

        if best_odd is None:
            return None

        odd = self._safe_float(
            best_odd.get(
                "odd",
                0,
            )
        )

        if odd <= 0:
            return None

        selected_market = str(
            best_odd.get(
                "market",
                "",
            )
        ).strip()

        selected_outcome = str(
            best_odd.get(
                "outcome",
                "",
            )
        ).strip()

        # ------------------------------------------------------
        # MÉDIA DO MERCADO
        # ------------------------------------------------------

        average_odd = (
            self._calculate_market_average(
                event=event,
                selected_outcome=selected_outcome,
                selected_market=selected_market,
            )
        )

        # ------------------------------------------------------
        # VARIAÇÃO
        # ------------------------------------------------------

        variation = (
            self._market_variation(
                odd,
                average_odd,
            )
        )

        # ------------------------------------------------------
        # PROBABILIDADE DE MERCADO
        # ------------------------------------------------------

        probability = (
            self._calculate_market_probability(
                event=event,
                selected_outcome=selected_outcome,
                selected_market=selected_market,
                selected_odd=odd,
            )
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------
        #
        # Agora o EV NÃO utiliza a própria odd para gerar
        # a probabilidade.
        #
        # Fórmula:
        #
        # EV = (probabilidade × odd) - 1
        #
        # Como probability está em percentual:
        #
        # EV = ((probabilidade / 100) × odd) - 1
        #
        # Exemplo:
        #
        # probabilidade = 35%
        # odd = 3.30
        #
        # EV = (0.35 × 3.30) - 1
        # EV = 0.155
        # EV = +15.5%
        #
        # ------------------------------------------------------

        probability_decimal = (
            probability / 100.0
        )

        expected_value = (
            (
                probability_decimal
                * odd
            )
            - 1.0
        ) * 100.0

        expected_value = round(
            expected_value,
            4,
        )

        # ------------------------------------------------------
        # VALUE BET
        # ------------------------------------------------------

        is_value = (
            valuebet_engine.is_value_bet(
                probability,
                odd,
            )
        )

        # ------------------------------------------------------
        # RISCO
        # ------------------------------------------------------

        risk = self._risk_level(
            probability,
            expected_value,
            variation,
        )

        # ------------------------------------------------------
        # ÍNDICE ODREAL
        # ------------------------------------------------------

        oddreal_index = (
            self._calculate_oddreal_index(
                probability=probability,
                expected_value=expected_value,
                market_variation=variation,
            )
        )

        # ------------------------------------------------------
        # RESULTADO
        # ------------------------------------------------------

        return {

            # ==================================================
            # IDENTIFICAÇÃO
            # ==================================================

            "id":
                event.get(
                    "id",
                    "",
                ),

            "event_id":
                event.get(
                    "id",
                    "",
                ),

            "sport_key":
                event.get(
                    "sport_key",
                    "",
                ),

            "sport_title":
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

            # ==================================================
            # MERCADO
            # ==================================================

            "selected_market":
                selected_market,

            "market":
                selected_market,

            "selected_outcome":
                selected_outcome,

            "outcome":
                selected_outcome,

            "selected_bookmaker":
                best_odd.get(
                    "bookmaker",
                    "",
                ),

            "bookmaker":
                best_odd.get(
                    "bookmaker",
                    "",
                ),

            "odd":
                round(
                    odd,
                    3,
                ),

            "best_odd":
                best_odd,

            # ==================================================
            # INDICADORES
            # ==================================================

            "probability":
                round(
                    probability,
                    3,
                ),

            "implied_probability":
                round(
                    probability,
                    3,
                ),

            "expected_value":
                round(
                    expected_value,
                    3,
                ),

            "ev":
                round(
                    expected_value,
                    3,
                ),

            "average_odd":
                round(
                    average_odd,
                    3,
                ),

            "market_variation":
                round(
                    variation,
                    3,
                ),

            "oddreal_index":
                oddreal_index,

            "confidence_level":
                self._confidence_level(
                    oddreal_index
                ),

            "risk":
                risk,

            "is_value_bet":
                is_value,

        }

    # ==========================================================
    # ÍNDICE ODREAL
    # ==========================================================

    @staticmethod
    def _calculate_oddreal_index(
        probability: float,
        expected_value: float,
        market_variation: float,
    ) -> int:
        """
        Calcula um índice padronizado de 0 a 100.

        O índice é um indicador interno e não uma
        probabilidade de vitória.
        """

        probability_score = min(
            max(
                Analyzer._normalize_probability(
                    probability
                ),
                0.0,
            ),
            100.0,
        )

        # EV negativo não recebe pontuação positiva.
        ev_score = min(
            max(
                expected_value * 2.0,
                0.0,
            ),
            100.0,
        )

        market_score = min(
            max(
                50.0
                + market_variation * 2.0,
                0.0,
            ),
            100.0,
        )

        index = (
            probability_score * 0.40
            + ev_score * 0.35
            + market_score * 0.25
        )

        return int(
            round(
                min(
                    max(
                        index,
                        0.0,
                    ),
                    100.0,
                )
            )
        )

    # ==========================================================
    # CONFIANÇA
    # ==========================================================

    @staticmethod
    def _confidence_level(
        index: int,
    ) -> str:

        if index >= 85:
            return "Muito Alta"

        if index >= 70:
            return "Alta"

        if index >= 55:
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # ANÁLISE EM LOTE
    # ==========================================================

    def analyze(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
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

            try:

                result = (
                    self.analyze_event(
                        event
                    )
                )

                if result is not None:

                    analyses.append(
                        result
                    )

            except Exception as exc:

                error(
                    "Erro ao analisar evento: "
                    f"{exc}"
                )

        info(
            f"{len(analyses)} "
            "eventos analisados."
        )

        return analyses

    # ==========================================================
    # VALUE BETS
    # ==========================================================

    def value_bets(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Identifica as Value Bets.
        """

        if not isinstance(
            analyses,
            list,
        ):
            return []

        return (
            valuebet_engine.analyze(
                analyses
            )
        )

    # ==========================================================
    # MELHOR OPORTUNIDADE
    # ==========================================================

    def best_opportunity(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not analyses:
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
            key=lambda item:
                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0,
                    )
                ),
        )

    # ==========================================================
    # MELHOR VALUE BET
    # ==========================================================

    def best_value_bet(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        opportunities = (
            self.value_bets(
                analyses
            )
        )

        return (
            valuebet_engine.best_value_bet(
                opportunities
            )
        )

    # ==========================================================
    # RESUMO
    # ==========================================================

    def summary(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Gera resumo das análises.
        """

        if not isinstance(
            analyses,
            list,
        ):
            analyses = []

        value_bets = (
            self.value_bets(
                analyses
            )
        )

        risks: Dict[
            str,
            int
        ] = {}

        for item in analyses:

            if not isinstance(
                item,
                dict,
            ):
                continue

            risk = str(
                item.get(
                    "risk",
                    "Desconhecido",
                )
            )

            risks[risk] = (
                risks.get(
                    risk,
                    0,
                )
                + 1
            )

        return {

            "total_analyses":
                len(analyses),

            "total_value_bets":
                len(value_bets),

            "average_oddreal_index":
                self._average_index(
                    analyses
                ),

            "average_expected_value":
                self._average_ev(
                    analyses
                ),

            "risk_distribution":
                risks,

        }

    # ==========================================================
    # MÉDIA DO ÍNDICE
    # ==========================================================

    @staticmethod
    def _average_index(
        analyses: List[
            Dict[str, Any]
        ],
    ) -> float:

        values = [

            Analyzer._safe_float(
                item.get(
                    "oddreal_index",
                    0,
                )
            )

            for item in analyses

            if isinstance(
                item,
                dict,
            )
        ]

        if not values:
            return 0.0

        return round(
            sum(values)
            / len(values),
            2,
        )

    # ==========================================================
    # MÉDIA DO EV
    # ==========================================================

    @staticmethod
    def _average_ev(
        analyses: List[
            Dict[str, Any]
        ],
    ) -> float:
        """
        Calcula o EV médio das análises.
        """

        values = [

            Analyzer._safe_float(
                item.get(
                    "expected_value",
                    0,
                )
            )

            for item in analyses

            if isinstance(
                item,
                dict,
            )
        ]

        if not values:
            return 0.0

        return round(
            sum(values)
            / len(values),
            3,
        )


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()
          
