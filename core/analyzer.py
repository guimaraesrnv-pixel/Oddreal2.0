"""
OddReal 2.0
Analyzer

Responsável por:
- analisar eventos preparados pelo Pipeline;
- identificar a melhor odd;
- calcular probabilidade de mercado normalizada;
- calcular EV usando probabilidade independente da odd escolhida;
- identificar Value Bets;
- calcular Índice OddReal;
- classificar risco e confiança.

IMPORTANTE:
A probabilidade utilizada para EV NÃO é derivada da própria odd escolhida.
Ela é estimada a partir do consenso das casas disponíveis no mercado.

Isso evita o erro matemático:

    odd -> probabilidade implícita -> EV -> Value Bet

que criava um ciclo.

O fluxo correto é:

    odds do mercado
        ↓
    probabilidade implícita
        ↓
    remoção da margem
        ↓
    probabilidade de mercado
        ↓
    EV
        ↓
    Value Bet
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

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
    # UTILITÁRIO NUMÉRICO
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

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
                bookmaker.get("title")
                or bookmaker.get("name")
                or bookmaker.get("key")
                or ""
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
    # COLETAR MERCADO
    # ==========================================================

    def _get_market_outcomes(
        self,
        event: Dict[str, Any],
        selected_market: str,
    ) -> Dict[str, List[float]]:
        """
        Reúne todas as odds disponíveis por seleção.

        Exemplo:

        {
            "Fenerbahce": [1.40, 1.42, 1.39],
            "Draw": [4.50, 4.70, 4.60],
            "SK Sturm Graz": [8.50, 8.20, 8.40]
        }

        Isso permite calcular o consenso do mercado.
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

        result: Dict[
            str,
            List[float]
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

                market_name = str(
                    market.get(
                        "key",
                        "",
                    )
                ).strip()

                if (
                    selected_market
                    and market_name
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

                    result.setdefault(
                        name,
                        []
                    ).append(
                        odd
                    )

        return result

    # ==========================================================
    # PROBABILIDADE DE MERCADO
    # ==========================================================

    def _calculate_fair_probability(
    self,
    event: Dict[str, Any],
    selected_market: str,
    selected_outcome: str,
 ) -> float:
    """
    Calcula uma probabilidade de mercado ajustada pela margem.

    Para cada bookmaker:
    1. coleta todas as seleções do mesmo mercado;
    2. converte odds em probabilidades implícitas;
    3. normaliza as probabilidades para remover o overround;
    4. obtém a probabilidade justa da seleção escolhida.

    Depois calcula a média entre os bookmakers válidos.

    Esta NÃO é uma previsão estatística independente.
    É uma estimativa baseada no consenso do mercado.
    """

    bookmakers = event.get("bookmakers", [])

    if not isinstance(bookmakers, list):
        return 0.0

    probabilities = []

    for bookmaker in bookmakers:

        if not isinstance(bookmaker, dict):
            continue

        markets = bookmaker.get("markets", [])

        if not isinstance(markets, list):
            continue

        for market in markets:

            if not isinstance(market, dict):
                continue

            market_key = str(
                market.get("key", "")
            ).strip()

            if market_key != selected_market:
                continue

            outcomes = market.get("outcomes", [])

            if not isinstance(outcomes, list):
                continue

            normalized = []

            for outcome in outcomes:

                if not isinstance(outcome, dict):
                    continue

                name = str(
                    outcome.get("name", "")
                ).strip()

                odd = self._safe_float(
                    outcome.get("price", 0)
                )

                if odd <= 0:
                    continue

                normalized.append(
                    {
                        "name": name,
                        "odd": odd,
                        "probability": 1.0 / odd,
                    }
                )

            if not normalized:
                continue

            total_probability = sum(
                item["probability"]
                for item in normalized
            )

            if total_probability <= 0:
                continue

            for item in normalized:

                if item["name"] == selected_outcome:

                    fair_probability = (
                        item["probability"]
                        / total_probability
                    ) * 100.0

                    probabilities.append(
                        fair_probability
                    )

                    break

    if not probabilities:
        return 0.0

    return round(
        sum(probabilities)
        / len(probabilities),
        4,
    )

    # ==========================================================
    # MÉDIA DE MERCADO
    # ==========================================================

    def _calculate_market_average(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
        selected_market: str,
    ) -> float:

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

                market_name = str(
                    market.get(
                        "key",
                        "",
                    )
                ).strip()

                if (
                    selected_market
                    and market_name
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
    # VARIAÇÃO DE MERCADO
    # ==========================================================

    @staticmethod
    def _market_variation(
        odd: float,
        average_odd: float,
    ) -> float:

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

        # Odds muito altas representam eventos
        # com baixa probabilidade de ocorrência.
        # Portanto, não classificamos automaticamente
        # como risco baixo só porque o EV é positivo.

        if (
            probability >= 65
            and expected_value >= 5
            and variation >= 0
        ):
            return "Moderado"

        if (
            probability >= 50
            and expected_value >= 0
        ):
            return "Moderado"

        return "Alto"

    # ==========================================================
    # ANÁLIÇÃO DE EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:

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

        if not selected_outcome:
            return None

        # ======================================================
        # PROBABILIDADE DE MERCADO
        # ======================================================

        market_probability = (
            self._calculate_market_probability(
                event,
                selected_market,
                selected_outcome,
            )
        )

        # ======================================================
        # FALLBACK
        # ======================================================

        # Se não houver casas suficientes para construir
        # uma probabilidade de mercado, NÃO inventamos
        # uma probabilidade.
        #
        # Nesse caso usamos a probabilidade implícita apenas
        # como referência e marcamos a fonte corretamente.

        if market_probability <= 0:

            probability = (
                valuebet_engine.implied_probability(
                    odd
                )
            )

            probability_source = (
                "implicit_odds_fallback"
            )

        else:

            probability = (
                market_probability
            )

            probability_source = (
                "normalized_market_consensus"
            )

        # ======================================================
        # EV
        # ======================================================

        expected_value = (
            valuebet_engine.expected_value(
                probability,
                odd,
            )
        )

        # ======================================================
        # MÉDIA
        # ======================================================

        average_odd = (
            self._calculate_market_average(
                event,
                selected_outcome,
                selected_market,
            )
        )

        variation = (
            self._market_variation(
                odd,
                average_odd,
            )
        )

        # ======================================================
        # VALUE BET
        # ======================================================

        is_value = (
            probability_source
            == "normalized_market_consensus"
            and valuebet_engine.is_value_bet(
                probability,
                odd,
            )
        )

        # ======================================================
        # ÍNDICE
        # ======================================================

        oddreal_index = (
            self._calculate_oddreal_index(
                probability=probability,
                expected_value=expected_value,
                market_variation=variation,
                probability_source=probability_source,
            )
        )

        risk = self._risk_level(
            probability,
            expected_value,
            variation,
        )

        # ======================================================
        # RESULTADO
        # ======================================================

        return {

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
            # PROBABILIDADE
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

            # --------------------------------------------------
            # EV
            # --------------------------------------------------

            "expected_value":
                round(
                    expected_value,
                    3,
                ),

            # --------------------------------------------------
            # MERCADO
            # --------------------------------------------------

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

            # --------------------------------------------------
            # ÍNDICE
            # --------------------------------------------------

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
        probability_source: str,
    ) -> int:

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

        # Se não temos uma probabilidade independente,
        # reduzimos drasticamente a confiança do índice.
        if (
            probability_source
            != "normalized_market_consensus"
        ):

            index *= 0.60

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

        if not isinstance(
            analyses,
            list,
        ):
            return []

        return valuebet_engine.analyze(
            analyses
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
