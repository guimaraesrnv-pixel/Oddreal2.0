"""
OddReal 2.0
Analyzer

Arquivo:
core/analyzer.py

Responsável por:
- Analisar eventos preparados pelo Pipeline;
- Agrupar odds por mercado e seleção;
- Calcular consenso de mercado;
- Estimar probabilidade justa;
- Calcular EV;
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

from typing import Any, Dict, List, Optional, Tuple

from modules.logger import info, error
from oddsengine.value import valuebet_engine


class Analyzer:
    """
    Camada central de análise quantitativa do OddReal 2.0.
    """

    # ==========================================================
    # CASAS PRIORITÁRIAS PARA O MERCADO BRASILEIRO
    # ==========================================================

    BRAZILIAN_BOOKMAKERS = {
        "betano",
        "bet365",
        "betfair",
        "sportingbet",
        "superbet",
        "novibet",
        "kto",
        "betnacional",
        "estrelabet",
        "pixbet",
        "betmgm",
        "rivalo",
        "brbet",
        "galera.bet",
        "galera bet",
        "flabet",
        "betsat",
        "vai de bet",
        "betsson",
        "betway",
    }

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    MIN_BOOKMAKERS_FOR_CONSENSUS = 3

    # Evita que uma cotação extremamente isolada
    # seja tratada automaticamente como oportunidade.
    MAX_MARKET_DEVIATION = 35.0

    # EV mínimo para Value Bet real.
    MIN_VALUE_EV = 5.0

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
    def _normalize_name(
        value: Any,
    ) -> str:
        """
        Normaliza nomes para comparação.
        """

        return (
            str(value or "")
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

    # ==========================================================
    # CASA BRASILEIRA
    # ==========================================================

    @classmethod
    def _is_brazilian_bookmaker(
        cls,
        bookmaker: Any,
    ) -> bool:
        """
        Verifica se a casa pertence ao conjunto
        prioritário do mercado brasileiro.

        A API pode fornecer title, key ou name.
        """

        if isinstance(
            bookmaker,
            dict,
        ):

            raw_name = (
                bookmaker.get("title")
                or bookmaker.get("name")
                or bookmaker.get("key")
                or ""
            )

        else:

            raw_name = bookmaker

        normalized = cls._normalize_name(
            raw_name
        )

        if not normalized:
            return False

        return normalized in cls.BRAZILIAN_BOOKMAKERS

    # ==========================================================
    # EXTRAÇÃO DAS ODDS
    # ==========================================================

    def _extract_all_odds(
        self,
        event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Extrai todas as odds preservando:

        - casa;
        - mercado;
        - seleção;
        - odd.

        A estrutura original do evento não é alterada.
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

        result: List[
            Dict[str, Any]
        ] = []

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

                market_name = (
                    market.get("key")
                    or market.get("name")
                    or ""
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

                    if odd <= 1:
                        continue

                    selection = str(
                        outcome.get(
                            "name",
                            "",
                        )
                    ).strip()

                    if not selection:
                        continue

                    result.append(
                        {
                            "odd": odd,
                            "bookmaker": bookmaker_name,
                            "market": market_name,
                            "outcome": selection,
                            "is_brazilian": (
                                self._is_brazilian_bookmaker(
                                    bookmaker
                                )
                            ),
                        }
                    )

        return result

    # ==========================================================
    # AGRUPAMENTO DE MERCADO
    # ==========================================================

    @staticmethod
    def _group_market_odds(
        odds: List[Dict[str, Any]],
    ) -> Dict[
        Tuple[str, str],
        List[Dict[str, Any]]
    ]:
        """
        Agrupa odds por:

            mercado + seleção

        Isso impede comparar:
        - Home contra Draw;
        - Over contra Under;
        - mercados diferentes.
        """

        groups: Dict[
            Tuple[str, str],
            List[Dict[str, Any]]
        ] = {}

        for item in odds:

            market = str(
                item.get(
                    "market",
                    "",
                )
            ).strip()

            outcome = str(
                item.get(
                    "outcome",
                    "",
                )
            ).strip()

            if not market or not outcome:
                continue

            key = (
                market.lower(),
                outcome.lower(),
            )

            groups.setdefault(
                key,
                [],
            ).append(item)

        return groups

    # ==========================================================
    # MÉDIA DAS ODDS
    # ==========================================================

    @staticmethod
    def _average(
        values: List[float],
    ) -> float:
        """
        Média aritmética segura.
        """

        valid = [
            value
            for value in values
            if value > 0
        ]

        if not valid:
            return 0.0

        return (
            sum(valid)
            / len(valid)
        )

    # ==========================================================
    # PROBABILIDADES IMPLÍCITAS
    # ==========================================================

    @staticmethod
    def _implied_probability_decimal(
        odd: float,
    ) -> float:
        """
        Probabilidade implícita em escala decimal.

        Exemplo:

        odd 2.00 -> 0.50
        odd 5.00 -> 0.20
        """

        if odd <= 0:
            return 0.0

        return 1.0 / odd

    # ==========================================================
    # PROBABILIDADE JUSTA
    # ==========================================================

    def _calculate_fair_probability(
        self,
        market_groups: Dict[
            Tuple[str, str],
            List[Dict[str, Any]]
        ],
        selected_market: str,
        selected_outcome: str,
    ) -> float:
        """
        Calcula uma probabilidade de consenso para
        uma seleção.

        Para mercados com múltiplas seleções, como h2h,
        remove a margem implícita das casas antes de
        calcular a probabilidade média.

        Retorno:
            percentual de 0 a 100.
        """

        selected_key = (
            selected_market.lower(),
            selected_outcome.lower(),
        )

        selected_prices = market_groups.get(
            selected_key,
            [],
        )

        if not selected_prices:
            return 0.0

        # ------------------------------------------------------
        # CASAS BRASILEIRAS PRIMEIRO
        # ------------------------------------------------------

        brazilian_prices = [
            item
            for item in selected_prices
            if item.get(
                "is_brazilian",
                False,
            )
        ]

        if len(brazilian_prices) >= self.MIN_BOOKMAKERS_FOR_CONSENSUS:

            usable_selected = (
                brazilian_prices
            )

        else:

            usable_selected = (
                selected_prices
            )

        # ------------------------------------------------------
        # LOCALIZA TODAS AS SELEÇÕES DO MESMO MERCADO
        # ------------------------------------------------------

        same_market: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        market_prefix = (
            selected_market.lower()
        )

        for (
            market_outcome,
            items,
        ) in market_groups.items():

            market_name, outcome_name = (
                market_outcome
            )

            if market_name != market_prefix:
                continue

            same_market[
                outcome_name
            ] = items

        # ------------------------------------------------------
        # SE EXISTE APENAS UMA SELEÇÃO,
        # NÃO É POSSÍVEL REMOVER VIG COM SEGURANÇA.
        # ------------------------------------------------------

        if len(same_market) <= 1:

            implied_values = [
                self._implied_probability_decimal(
                    self._safe_float(
                        item.get(
                            "odd",
                            0,
                        )
                    )
                )
                for item in usable_selected
            ]

            average_probability = self._average(
                implied_values
            )

            return round(
                average_probability * 100.0,
                4,
            )

        # ------------------------------------------------------
        # CALCULA A MARGEM DE CADA CASA
        # ------------------------------------------------------

        bookmaker_probabilities: Dict[
            str,
            Dict[str, float]
        ] = {}

        for outcome_name, items in same_market.items():

            for item in items:

                bookmaker = self._normalize_name(
                    item.get(
                        "bookmaker",
                        "",
                    )
                )

                odd = self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                )

                if odd <= 1:
                    continue

                probability = (
                    self._implied_probability_decimal(
                        odd
                    )
                )

                bookmaker_probabilities.setdefault(
                    bookmaker,
                    {}
                )

                bookmaker_probabilities[
                    bookmaker
                ][
                    outcome_name
                ] = probability

        # ------------------------------------------------------
        # NORMALIZAÇÃO DO VIG
        # ------------------------------------------------------

        fair_probabilities: List[
            float
        ] = []

        selected_outcome_key = (
            selected_outcome.lower()
        )

        for bookmaker, outcomes in (
            bookmaker_probabilities.items()
        ):

            total_probability = sum(
                outcomes.values()
            )

            selected_probability = outcomes.get(
                selected_outcome_key
            )

            if (
                selected_probability is None
                or total_probability <= 0
            ):
                continue

            fair_probability = (
                selected_probability
                / total_probability
            )

            fair_probabilities.append(
                fair_probability
            )

        # ------------------------------------------------------
        # FILTRO DE CASAS BRASILEIRAS
        # ------------------------------------------------------

        if len(brazilian_prices) >= self.MIN_BOOKMAKERS_FOR_CONSENSUS:

            brazilian_names = {
                self._normalize_name(
                    item.get(
                        "bookmaker",
                        "",
                    )
                )
                for item in brazilian_prices
            }

            filtered = []

            for item in fair_probabilities:
                filtered.append(item)

            if filtered:

                fair_probabilities = filtered

        # ------------------------------------------------------
        # FALLBACK
        # ------------------------------------------------------

        if not fair_probabilities:

            implied_values = [
                self._implied_probability_decimal(
                    self._safe_float(
                        item.get(
                            "odd",
                            0,
                        )
                    )
                )
                for item in usable_selected
            ]

            return round(
                self._average(
                    implied_values
                ) * 100.0,
                4,
            )

        return round(
            self._average(
                fair_probabilities
            ) * 100.0,
            4,
        )

    # ==========================================================
    # MELHOR PREÇO
    # ==========================================================

    def _get_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Seleciona a melhor odd somente depois de
        considerar mercado e seleção.

        Não escolhe simplesmente a maior odd do evento.
        """

        odds = self._extract_all_odds(
            event
        )

        if not odds:
            return None

        candidates = []

        for item in odds:

            if (
                str(
                    item.get(
                        "market",
                        ""
                    )
                ).lower()
                != "h2h"
            ):
                continue

            candidates.append(
                item
            )

        if not candidates:

            candidates = odds

        # ------------------------------------------------------
        # Procura a seleção com melhor potencial
        # dentro do mercado.
        # ------------------------------------------------------

        return max(
            candidates,
            key=lambda item:
                self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                ),
        )

    # ==========================================================
    # VARIAÇÃO DO MERCADO
    # ==========================================================

    @staticmethod
    def _market_variation(
        odd: float,
        fair_odd: float,
    ) -> float:
        """
        Mede quanto a odd oferecida está acima/abaixo
        da odd justa.
        """

        if fair_odd <= 0:
            return 0.0

        return round(
            (
                (
                    odd
                    - fair_odd
                )
                / fair_odd
            ) * 100.0,
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
        Classificação conservadora.

        Importante:
        risco não significa probabilidade de perda
        de forma determinística.
        """

        if (
            probability >= 65
            and expected_value >= 8
            and variation >= 5
        ):
            return "Baixo"

        if (
            probability >= 45
            and expected_value >= 5
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
        Índice interno de 0 a 100.

        O índice não é probabilidade de vitória.

        Componentes:
        - probabilidade justa;
        - EV;
        - vantagem sobre o preço justo.
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
                expected_value * 3.0,
                0.0,
            ),
            100.0,
        )

        market_score = min(
            max(
                50.0
                + market_variation,
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
    # ANALISAR EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        if not isinstance(
            event,
            dict,
        ):
            return None

        all_odds = self._extract_all_odds(
            event
        )

        if not all_odds:
            return None

        market_groups = (
            self._group_market_odds(
                all_odds
            )
        )

        # ------------------------------------------------------
        # MELHOR ODD
        # ------------------------------------------------------

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

        if odd <= 1:
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
        # PROBABILIDADE JUSTA
        # ------------------------------------------------------

        probability = (
            self._calculate_fair_probability(
                market_groups,
                selected_market,
                selected_outcome,
            )
        )

        if probability <= 0:
            return None

        # ------------------------------------------------------
        # ODD JUSTA
        # ------------------------------------------------------

        fair_odd = (
            100.0
            / probability
        )

        # ------------------------------------------------------
        # EV REAL
        # ------------------------------------------------------

        expected_value = (
            (
                probability
                / 100.0
            )
            * odd
            - 1.0
        ) * 100.0

        expected_value = round(
            expected_value,
            4,
        )

        # ------------------------------------------------------
        # VARIAÇÃO
        # ------------------------------------------------------

        variation = (
            self._market_variation(
                odd,
                fair_odd,
            )
        )

        # ------------------------------------------------------
        # VALUE BET
        # ------------------------------------------------------

        is_value = (
            expected_value
            >= self.MIN_VALUE_EV
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
        # ÍNDICE
        # ------------------------------------------------------

        oddreal_index = (
            self._calculate_oddreal_index(
                probability=probability,
                expected_value=expected_value,
                market_variation=variation,
            )
        )

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

            "fair_odd":
                round(
                    fair_odd,
                    3,
                ),

            "best_odd":
                best_odd,

            "probability":
                round(
                    probability,
                    3,
                ),

            "implied_probability":
                round(
                    100.0 / odd,
                    3,
                ),

            "expected_value":
                round(
                    expected_value,
                    3,
                ),

            "average_odd":
                round(
                    fair_odd,
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

            "bookmaker_count":
                len(
                    all_odds
                ),

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

                result = self.analyze_event(
                    event
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

        opportunities = self.value_bets(
            analyses
        )

        return valuebet_engine.best_value_bet(
            opportunities
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

        value_bets = self.value_bets(
            analyses
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
