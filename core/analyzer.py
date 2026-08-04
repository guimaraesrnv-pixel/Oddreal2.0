"""
OddReal 2.0
Analyzer

Arquivo:
core/analyzer.py

Responsável por:
- Analisar eventos preparados pelo Pipeline;
- Selecionar a melhor odd;
- Calcular indicadores básicos da análise;
- Integrar o ValueBetEngine;
- Identificar Value Bets;
- Encontrar melhores oportunidades;
- Gerar resumo das análises.

IMPORTANTE:
- Não consulta a The Odds API.
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
                    0,
                )
            )

            if odd > 0:

                return {

                    "odd": odd,

                    "bookmaker":
                        existing.get(
                            "bookmaker",
                            "",
                        ),

                    "market":
                        existing.get(
                            "market",
                            "",
                        ),

                    "outcome":
                        existing.get(
                            "outcome",
                            "",
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

        best = None

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

                        "bookmaker":
                            bookmaker_name,

                        "market":
                            market_name,

                        "outcome":
                            outcome.get(
                                "name",
                                "",
                            ),

                    }

                    if (
                        best is None
                        or odd > best["odd"]
                    ):

                        best = candidate

        return best

    # ==========================================================
    # MÉDIA DE MERCADO
    # ==========================================================

    def _calculate_market_average(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
    ) -> float:
        """
        Calcula a média das odds para a mesma seleção.

        Isso evita comparar seleções diferentes entre si.
        """

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            return 0.0

        prices: List[
            float
        ] = []

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

                    if (
                        name
                        != selected_outcome
                    ):

                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if price > 0:

                        prices.append(
                            price
                        )

        if not prices:

            return 0.0

        return round(
            sum(prices)
            / len(prices),
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
            * 100,
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

        selected_outcome = str(
            best_odd.get(
                "outcome",
                "",
            )
        ).strip()

        average_odd = (
            self._calculate_market_average(
                event,
                selected_outcome,
            )
        )

        variation = (
            self._market_variation(
                odd,
                average_odd,
            )
        )

        # ------------------------------------------------------
        # PROBABILIDADE BASE
        # ------------------------------------------------------
        #
        # Neste estágio utilizamos a probabilidade implícita.
        # O Analyzer não inventa uma probabilidade externa.
        #
        # Um módulo estatístico futuro poderá substituir essa
        # estimativa por uma probabilidade modelada.
        #

        probability = (
            valuebet_engine.implied_probability(
                odd
            )
        )

        expected_value = (
            valuebet_engine.expected_value(
                probability,
                odd,
            )
        )

        is_value = (
            valuebet_engine.is_value_bet(
                probability,
                odd,
            )
        )

        risk = self._risk_level(
            probability,
            expected_value,
            variation,
        )

        # ------------------------------------------------------
        # ÍNDICE ODREAL
        # ------------------------------------------------------

        oddreal_index = self._calculate_oddreal_index(
            probability=probability,
            expected_value=expected_value,
            market_variation=variation,
        )

        return {

            # --------------------------------------------------
            # IDENTIFICAÇÃO
            # --------------------------------------------------

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

            # --------------------------------------------------
            # MERCADO
            # --------------------------------------------------

            "selected_market":
                best_odd.get(
                    "market",
                    "",
                ),

            "selected_outcome":
                selected_outcome,

            "selected_bookmaker":
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

            # --------------------------------------------------
            # INDICADORES
            # --------------------------------------------------

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
                probability,
                0.0,
            ),
            100.0,
        )

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

            float(
                item.get(
                    "oddreal_index",
                    0,
                )
                or 0
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
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()
