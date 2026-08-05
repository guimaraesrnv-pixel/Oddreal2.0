"""
OddReal 2.0
Analyzer

Arquivo:
core/analyzer.py

Responsável por:
- Analisar eventos preparados pelo Pipeline;
- Encontrar a melhor odd por seleção;
- Calcular probabilidade de consenso;
- Remover margem do mercado;
- Calcular EV usando probabilidade independente da melhor odd;
- Calcular variação de mercado;
- Integrar o ValueBetEngine;
- Identificar Value Bets;
- Encontrar melhores oportunidades.

IMPORTANTE:
- Não consulta a The Odds API.
- Não contém API Key.
- Não utiliza IA para cálculos.
- A IA permanece na camada interpretativa.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from modules.logger import info, error
from oddsengine.value import valuebet_engine


class Analyzer:
    """
    Camada central de análise quantitativa do OddReal 2.0.
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

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        """
        Normaliza textos usados para comparação.
        """

        return str(
            value or ""
        ).strip().lower()

    # ==========================================================
    # COLETA DAS ODDS DO EVENTO
    # ==========================================================

    def _collect_market_outcomes(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, List[float]]:
        """
        Coleta todas as odds disponíveis por seleção.

        Estrutura retornada:

        {
            "home": [2.10, 2.15, 2.05],
            "draw": [3.40, 3.50],
            "away": [3.80, 3.90]
        }

        A função preserva apenas odds do mesmo mercado.
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

        markets_data: Dict[
            str,
            Dict[str, List[float]]
        ] = {}

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
                    or ""
                ).strip()

                if not market_key:
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

                if market_key not in markets_data:

                    markets_data[
                        market_key
                    ] = {}

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
                        or ""
                    ).strip()

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if (
                        not outcome_name
                        or price <= 1.0
                    ):
                        continue

                    markets_data[
                        market_key
                    ].setdefault(
                        outcome_name,
                        [],
                    ).append(
                        price
                    )

        return self._select_best_market(
            markets_data
        )

    # ==========================================================
    # SELECIONAR MERCADO MAIS COMPLETO
    # ==========================================================

    @staticmethod
    def _select_best_market(
        markets_data: Dict[
            str,
            Dict[str, List[float]]
        ],
    ) -> Dict[str, List[float]]:
        """
        Seleciona o mercado mais adequado.

        Prioridade:
        1. h2h
        2. primeiro mercado disponível

        Isso evita misturar mercados diferentes.
        """

        if not markets_data:
            return {}

        if "h2h" in markets_data:

            return markets_data["h2h"]

        first_market = next(
            iter(markets_data.values()),
            {},
        )

        return first_market

    # ==========================================================
    # MELHOR ODD
    # ==========================================================

    def _get_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra a maior odd disponível no evento.

        Importante:
        a melhor odd continua sendo selecionada por resultado,
        mas agora o cálculo de probabilidade é feito
        separadamente através do consenso do mercado.
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
        selected_market: str = "h2h",
    ) -> float:
        """
        Calcula a média das odds da mesma seleção
        dentro do mesmo mercado.
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

        prices: List[float] = []

        target_outcome = (
            self._normalize_text(
                selected_outcome
            )
        )

        target_market = (
            self._normalize_text(
                selected_market
            )
        )

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

                market_name = (
                    self._normalize_text(
                        market.get(
                            "key",
                            "",
                        )
                    )
                )

                if (
                    target_market
                    and market_name
                    != target_market
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

                    name = (
                        self._normalize_text(
                            outcome.get(
                                "name",
                                "",
                            )
                        )
                    )

                    if name != target_outcome:
                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if price > 1.0:

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
    # PROBABILIDADE DE CONSENSO
    # ==========================================================

    def _calculate_consensus_probability(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
        selected_market: str = "h2h",
    ) -> float:
        """
        Calcula a probabilidade de consenso do mercado.

        Processo:

        1. Coleta as melhores odds de cada seleção;
        2. Converte odds em probabilidades implícitas;
        3. Soma as probabilidades;
        4. Remove a margem do mercado;
        5. Retorna a probabilidade normalizada
           da seleção escolhida.

        Exemplo:

            Casa A:
            Time A = 2.00
            Empate = 3.50
            Time B = 4.00

        As probabilidades são normalizadas para que
        o conjunto some aproximadamente 100%.
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

        target_market = (
            self._normalize_text(
                selected_market
            )
        )

        target_outcome = (
            self._normalize_text(
                selected_outcome
            )
        )

        # ------------------------------------------------------
        # Melhor odd disponível para cada seleção
        # ------------------------------------------------------

        best_prices: Dict[
            str,
            float
        ] = {}

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

                market_name = (
                    self._normalize_text(
                        market.get(
                            "key",
                            "",
                        )
                    )
                )

                if (
                    target_market
                    and market_name
                    != target_market
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
                        or ""
                    ).strip()

                    normalized_name = (
                        self._normalize_text(
                            name
                        )
                    )

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if (
                        not normalized_name
                        or price <= 1.0
                    ):
                        continue

                    current = best_prices.get(
                        normalized_name
                    )

                    if (
                        current is None
                        or price > current
                    ):

                        best_prices[
                            normalized_name
                        ] = price

        if not best_prices:
            return 0.0

        # ------------------------------------------------------
        # Probabilidades implícitas
        # ------------------------------------------------------

        implied: Dict[
            str,
            float
        ] = {}

        for name, price in best_prices.items():

            implied[name] = (
                1.0 / price
            )

        total_probability = sum(
            implied.values()
        )

        if total_probability <= 0:
            return 0.0

        selected_probability = implied.get(
            target_outcome,
            0.0,
        )

        if selected_probability <= 0:
            return 0.0

        # ------------------------------------------------------
        # Remoção da margem
        # ------------------------------------------------------

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
    # VARIAÇÃO DE MERCADO
    # ==========================================================

    @staticmethod
    def _market_variation(
        odd: float,
        average_odd: float,
    ) -> float:
        """
        Mede quanto a melhor odd está acima ou abaixo
        da média das casas para a mesma seleção.

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
    # RISCO
    # ==========================================================

    @staticmethod
    def _risk_level(
        probability: float,
        expected_value: float,
        variation: float,
    ) -> str:
        """
        Classificação quantitativa simplificada.
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
    # ÍNDICE ODREAL
    # ==========================================================

    @staticmethod
    def _calculate_oddreal_index(
        probability: float,
        expected_value: float,
        market_variation: float,
    ) -> int:
        """
        Índice interno OddReal de 0 a 100.

        Componentes:

        - Probabilidade de consenso;
        - EV;
        - diferença da melhor odd para a média.

        O índice NÃO representa probabilidade de vitória.
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
    # ANÁLISE DE UM EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Analisa um evento individual.

        O ponto mais importante desta implementação:

        A probabilidade NÃO é mais calculada pela própria
        melhor odd.

        Ela vem do consenso normalizado do mercado.

        Depois:

            EV =
                probabilidade_consenso
                × melhor_odd
                - 100
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

        if odd <= 1.0:
            return None

        selected_outcome = str(
            best_odd.get(
                "outcome",
                "",
            )
            or ""
        ).strip()

        selected_market = str(
            best_odd.get(
                "market",
                "h2h",
            )
            or "h2h"
        ).strip()

        # ------------------------------------------------------
        # MÉDIA DO MERCADO
        # ------------------------------------------------------

        average_odd = (
            self._calculate_market_average(
                event,
                selected_outcome,
                selected_market,
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
        # PROBABILIDADE DE CONSENSO
        # ------------------------------------------------------

        probability = (
            self._calculate_consensus_probability(
                event,
                selected_outcome,
                selected_market,
            )
        )

        # ------------------------------------------------------
        # FALLBACK
        # ------------------------------------------------------
        #
        # Se o mercado não possuir dados suficientes para
        # normalização, usamos a probabilidade implícita
        # somente como fallback técnico.
        #
        # Isso evita quebrar a análise, mas o resultado fica
        # marcado no campo probability_source.
        #

        probability_source = (
            "market_consensus"
        )

        if probability <= 0:

            probability = (
                valuebet_engine.implied_probability(
                    odd
                )
            )

            probability_source = (
                "implied_fallback"
            )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        expected_value = (
    valuebet_engine.expected_value(
        probability,
        odd,
    )
)

info(
    "ODDREAL DEBUG | "
    f"{event.get('home_team', '')} × "
    f"{event.get('away_team', '')} | "
    f"odd={odd:.3f} | "
    f"probability={probability:.3f}% | "
    f"source={probability_source} | "
    f"EV={expected_value:.3f}%"
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
                selected_market,

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
                    valuebet_engine.implied_probability(
                        odd
                    ),
                    3,
                ),

            "probability_source":
                probability_source,

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
        Analisa todos os eventos.
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
        Identifica Value Bets.
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
