"""
OddReal 2.0
Analyzer

Motor central de análise quantitativa.

Responsável por:

- consolidar odds;
- calcular consenso de mercado;
- remover overround;
- calcular probabilidade estimada;
- calcular EV;
- calcular Índice OddReal;
- classificar confiança;
- classificar risco;
- identificar Value Bets;
- identificar melhor oportunidade;
- gerar resumo estatístico.

Este módulo:

- NÃO consulta API;
- NÃO utiliza IA;
- NÃO altera bookmakers;
- NÃO depende do Streamlit.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error


class Analyzer:
    """
    Motor central de análise quantitativa do OddReal 2.0.
    """

    # ==========================================================
    # CONFIGURAÇÕES
    # ==========================================================

    VALUE_BET_MIN_EV = 5.0

    MIN_OPPORTUNITY_INDEX = 50.0

    PRIMARY_MARKETS = {
        "h2h",
        "totals",
        "spreads",
    }

    def __init__(self) -> None:

        info(
            "Analyzer OddReal 2.0 iniciado."
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
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        EV = ((P / 100) × odd - 1) × 100
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if probability <= 0.0:
            return 0.0

        if odd <= 1.0:
            return 0.0

        probability = min(
            probability,
            100.0,
        )

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

    def _is_value_bet(
        self,
        expected_value: float,
    ) -> bool:

        expected_value = self._safe_float(
            expected_value
        )

        return (
            expected_value
            >= self.VALUE_BET_MIN_EV
        )

    # ==========================================================
    # RISCO
    # ==========================================================

    def _risk_level(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:
        """
        Risco baseado principalmente na probabilidade
        e na odd.

        Risco não determina Value Bet.
        """

        odd = self._safe_float(
            odd
        )

        probability = self._safe_float(
            probability
        )

        index = self._safe_float(
            index
        )

        if odd >= 8.0:
            return "Alto"

        if probability < 15.0:
            return "Alto"

        if probability < 25.0:
            return "Alto"

        if index < 40.0:
            return "Alto"

        if odd >= 4.0:
            return "Moderado"

        if index < 65.0:
            return "Moderado"

        return "Baixo"

    # Compatibilidade.
    def _risk(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:

        return self._risk_level(
            odd,
            probability,
            index,
        )

    # ==========================================================
    # CONFIANÇA
    # ==========================================================

    def _confidence_level(
        self,
        index: float,
    ) -> str:

        index = self._safe_float(
            index
        )

        if index >= 70.0:
            return "Alta"

        if index >= 45.0:
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # ÍNDICE ODdREAL
    # ==========================================================

    def _calculate_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int,
    ) -> float:
        """
        Índice OddReal de 0 a 100.

        IMPORTANTE:

        EV negativo NÃO recebe bônus.

        Além disso, quando EV é negativo,
        o índice é limitado para impedir que uma
        seleção negativa apareça como grande
        oportunidade no dashboard.
        """

        probability = max(
            0.0,
            min(
                100.0,
                self._safe_float(
                    probability
                ),
            ),
        )

        odd = self._safe_float(
            odd
        )

        expected_value = self._safe_float(
            expected_value
        )

        market_count = max(
            0,
            int(
                market_count
            ),
        )

        # ------------------------------------------------------
        # PROBABILIDADE
        # ------------------------------------------------------

        probability_score = min(
            60.0,
            probability * 0.60,
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        if expected_value > 0.0:

            ev_score = min(
                30.0,
                expected_value * 1.5,
            )

        else:

            ev_score = 0.0

        # ------------------------------------------------------
        # ROBUSTEZ DE MERCADO
        # ------------------------------------------------------

        market_score = min(
            10.0,
            market_count * 2.0,
        )

        raw_index = (
            probability_score
            + ev_score
            + market_score
        )

        # ------------------------------------------------------
        # PENALIZAÇÃO DE EV NEGATIVO
        # ------------------------------------------------------

        if expected_value < 0.0:

            # Uma oportunidade com EV negativo
            # nunca deve parecer uma oportunidade
            # excepcional.

            raw_index *= 0.60

        # ------------------------------------------------------
        # ODD EXTREMAMENTE ALTA
        # ------------------------------------------------------

        if odd >= 8.0:

            raw_index *= 0.90

        return round(
            max(
                0.0,
                min(
                    100.0,
                    raw_index,
                ),
            ),
            2,
        )

    # Compatibilidade.
    def _oddreal_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int = 0,
    ) -> float:

        return self._calculate_index(
            probability=probability,
            odd=odd,
            expected_value=expected_value,
            market_count=market_count,
        )

    # ==========================================================
    # EXTRAÇÃO DE MERCADOS
    # ==========================================================

    def _extract_market_data(
        self,
        event: Dict[str, Any],
    ) -> Dict[
        str,
        Dict[
            str,
            Dict[str, Any]
        ]
    ]:
        """
        Estrutura:

        {
            mercado: {
                seleção: {
                    odds: [],
                    bookmakers: []
                }
            }
        }
        """

        result: Dict[
            str,
            Dict[
                str,
                Dict[str, Any]
            ]
        ] = {}

        market_odds = event.get(
            "market_odds",
            [],
        )

        if not isinstance(
            market_odds,
            list,
        ):
            return result

        for item in market_odds:

            if not isinstance(
                item,
                dict,
            ):
                continue

            market = str(
                item.get(
                    "market",
                    "",
                )
            ).strip()

            outcome = str(
                item.get(
                    "outcome",
                    item.get(
                        "name",
                        "",
                    ),
                )
            ).strip()

            bookmaker = str(
                item.get(
                    "bookmaker",
                    "",
                )
            ).strip()

            odd = self._safe_float(
                item.get(
                    "odd",
                    item.get(
                        "price",
                        0.0,
                    ),
                )
            )

            if not market:
                continue

            if not outcome:
                continue

            if not bookmaker:
                continue

            if odd <= 1.0:
                continue

            result.setdefault(
                market,
                {}
            )

            result[
                market
            ].setdefault(
                outcome,
                {
                    "odds": [],
                    "bookmakers": [],
                },
            )

            result[
                market
            ][
                outcome
            ][
                "odds"
            ].append(
                odd
            )

            result[
                market
            ][
                outcome
            ][
                "bookmakers"
            ].append(
                {
                    "name": bookmaker,
                    "odd": odd,
                }
            )

        return result

    # ==========================================================
    # MELHOR BOOKMAKER
    # ==========================================================

    @staticmethod
    def _best_bookmaker(
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        valid: List[
            Dict[str, Any]
        ] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            odd = Analyzer._safe_float(
                bookmaker.get(
                    "odd",
                    0.0,
                )
            )

            if odd > 1.0:
                valid.append(
                    bookmaker
                )

        if not valid:
            return None

        return max(
            valid,
            key=lambda item:
            Analyzer._safe_float(
                item.get(
                    "odd",
                    0.0,
                )
            ),
        )

    # ==========================================================
    # CONSENSO DE MERCADO
    # ==========================================================

    def _market_consensus(
        self,
        outcomes: Dict[
            str,
            Dict[str, Any]
        ],
    ) -> Dict[str, float]:
        """
        Calcula a probabilidade de mercado de forma
        mais correta.

        Para cada bookmaker:

        1. coleta todas as seleções;
        2. calcula probabilidade implícita;
        3. remove o overround;
        4. produz uma distribuição de 100%.

        Depois:

        5. faz a média das probabilidades normalizadas
           entre os bookmakers.

        Isso evita usar simplesmente a média das odds
        para criar uma probabilidade.
        """

        bookmaker_markets: Dict[
            str,
            Dict[str, float]
        ] = {}

        for outcome_name, data in outcomes.items():

            bookmakers = data.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):
                continue

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                bookmaker_name = str(
                    bookmaker.get(
                        "name",
                        "",
                    )
                ).strip()

                odd = self._safe_float(
                    bookmaker.get(
                        "odd",
                        0.0,
                    )
                )

                if not bookmaker_name:
                    continue

                if odd <= 1.0:
                    continue

                bookmaker_markets.setdefault(
                    bookmaker_name,
                    {}
                )

                bookmaker_markets[
                    bookmaker_name
                ][
                    outcome_name
                ] = self.implied_probability(
                    odd
                )

        normalized_by_outcome: Dict[
            str,
            List[float]
        ] = {}

        for (
            bookmaker_name,
            probabilities,
        ) in bookmaker_markets.items():

            total = sum(
                probabilities.values()
            )

            if total <= 0.0:
                continue

            for (
                outcome_name,
                probability,
            ) in probabilities.items():

                normalized = (
                    probability
                    / total
                ) * 100.0

                normalized_by_outcome.setdefault(
                    outcome_name,
                    []
                ).append(
                    normalized
                )

        consensus: Dict[
            str,
            float
        ] = {}

        for (
            outcome_name,
            values,
        ) in normalized_by_outcome.items():

            if not values:
                continue

            consensus[
                outcome_name
            ] = round(
                sum(values)
                / len(values),
                4,
            )

        # ------------------------------------------------------
        # Correção final de soma
        # ------------------------------------------------------

        total_consensus = sum(
            consensus.values()
        )

        if total_consensus <= 0.0:
            return {}

        for outcome_name in list(
            consensus.keys()
        ):

            consensus[
                outcome_name
            ] = round(
                (
                    consensus[
                        outcome_name
                    ]
                    / total_consensus
                )
                * 100.0,
                4,
            )

        return consensus

    # ==========================================================
    # ANÁLISE GERAL
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

                results = (
                    self._analyze_event(
                        event
                    )
                )

                analyses.extend(
                    results
                )

            except Exception as exc:

                error(
                    "Erro ao analisar "
                    f"evento: {exc}"
                )

        info(
            f"{len(events)} eventos analisados."
        )

        return analyses

    # ==========================================================
    # ANÁLISE INDIVIDUAL
    # ==========================================================

    def _analyze_event(
        self,
        event: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            event,
            dict,
        ):
            return []

        event_id = event.get(
            "id",
            event.get(
                "event_id",
                "",
            ),
        )

        home_team = event.get(
            "home_team",
            "Casa",
        )

        away_team = event.get(
            "away_team",
            "Fora",
        )

        market_data = (
            self._extract_market_data(
                event
            )
        )

        results: List[
            Dict[str, Any]
        ] = []

        for (
            market,
            outcomes,
        ) in market_data.items():

            # --------------------------------------------------
            # CONSENSO
            # --------------------------------------------------

            probabilities = (
                self._market_consensus(
                    outcomes
                )
            )

            if not probabilities:
                continue

            # --------------------------------------------------
            # SELEÇÕES
            # --------------------------------------------------

            for (
                outcome_name,
                data,
            ) in outcomes.items():

                bookmakers = data.get(
                    "bookmakers",
                    [],
                )

                if not isinstance(
                    bookmakers,
                    list,
                ):
                    continue

                if not bookmakers:
                    continue

                best_bookmaker = (
                    self._best_bookmaker(
                        bookmakers
                    )
                )

                if best_bookmaker is None:
                    continue

                best_odd = (
                    self._safe_float(
                        best_bookmaker.get(
                            "odd",
                            0.0,
                        )
                    )
                )

                if best_odd <= 1.0:
                    continue

                probability = (
                    self._safe_float(
                        probabilities.get(
                            outcome_name,
                            0.0,
                        )
                    )
                )

                if probability <= 0.0:
                    continue

                # ------------------------------------------------
                # EV
                # ------------------------------------------------

                expected_value = (
                    self.expected_value(
                        probability,
                        best_odd,
                    )
                )

                # ------------------------------------------------
                # ÍNDICE
                # ------------------------------------------------

                oddreal_index = (
                    self._calculate_index(
                        probability=probability,
                        odd=best_odd,
                        expected_value=expected_value,
                        market_count=len(
                            bookmakers
                        ),
                    )
                )

                # ------------------------------------------------
                # CONFIANÇA
                # ------------------------------------------------

                confidence = (
                    self._confidence_level(
                        oddreal_index
                    )
                )

                # ------------------------------------------------
                # RISCO
                # ------------------------------------------------

                risk = (
                    self._risk_level(
                        odd=best_odd,
                        probability=probability,
                        index=oddreal_index,
                    )
                )

                # ------------------------------------------------
                # VALUE BET
                # ------------------------------------------------

                is_value = (
                    self._is_value_bet(
                        expected_value
                    )
                )

                odds = data.get(
                    "odds",
                    [],
                )

                average_odd = (
                    sum(odds)
                    / len(odds)
                    if odds
                    else 0.0
                )

                variation = (
                    self._variation(
                        odds
                    )
                )

                # ------------------------------------------------
                # RESULTADO
                # ------------------------------------------------

                analysis = {

                    "event_id":
                        event_id,

                    "id":
                        event_id,

                    "home_team":
                        home_team,

                    "away_team":
                        away_team,

                    "market":
                        market,

                    "selected_market":
                        market,

                    "outcome":
                        outcome_name,

                    "selection":
                        outcome_name,

                    "selected_outcome":
                        outcome_name,

                    "bookmaker":
                        best_bookmaker.get(
                            "name",
                            "Desconhecida",
                        ),

                    "selected_bookmaker":
                        best_bookmaker.get(
                            "name",
                            "Desconhecida",
                        ),

                    "odd":
                        round(
                            best_odd,
                            3,
                        ),

                    "best_odd":
                        round(
                            best_odd,
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

                    "probability_source":
                        "bookmaker_consensus",

                    "implied_probability":
                        round(
                            self.implied_probability(
                                best_odd
                            ),
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
                        confidence,

                    "confidence":
                        confidence,

                    "risk":
                        risk,

                    "is_value_bet":
                        is_value,

                    "value_classification":
                        (
                            "Value Bet"
                            if is_value
                            else (
                                "Positivo"
                                if expected_value > 0
                                else "Sem Valor"
                            )
                        ),

                    "market_count":
                        len(
                            bookmakers
                        ),

                    "available_bookmakers":
                        [
                            bookmaker.get(
                                "name",
                                "",
                            )
                            for bookmaker
                            in bookmakers
                            if isinstance(
                                bookmaker,
                                dict,
                            )
                        ],
                }

                results.append(
                    analysis
                )

        return results

    # ==========================================================
    # VARIAÇÃO
    # ==========================================================

    @staticmethod
    def _variation(
        odds: List[float],
    ) -> float:

        valid: List[
            float
        ] = []

        for odd in odds:

            try:

                value = float(
                    odd
                )

                if value > 1.0:

                    valid.append(
                        value
                    )

            except (
                TypeError,
                ValueError,
            ):

                continue

        if len(valid) < 2:
            return 0.0

        minimum = min(
            valid
        )

        maximum = max(
            valid
        )

        if minimum <= 0.0:
            return 0.0

        return round(
            (
                (
                    maximum
                    - minimum
                )
                / minimum
            )
            * 100.0,
            4,
        )

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

        values: List[
            Dict[str, Any]
        ] = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            ev = self._safe_float(
                analysis.get(
                    "expected_value",
                    0.0,
                )
            )

            is_value = (
                ev
                >= self.VALUE_BET_MIN_EV
            )

            analysis[
                "is_value_bet"
            ] = is_value

            if is_value:

                values.append(
                    analysis
                )

        values.sort(
            key=lambda item:
            self._safe_float(
                item.get(
                    "expected_value",
                    0.0,
                )
            ),
            reverse=True,
        )

        info(
            f"{len(values)} "
            "Value Bets encontradas."
        )

        return values

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

        if not isinstance(
            analyses,
            list,
        ):
            return None

        valid = [

            item

            for item in analyses

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
                > 0.0
            )
        ]

        # Se nenhuma seleção tiver EV positivo,
        # não inventamos uma "oportunidade".
        if not valid:
            return None

        return max(
            valid,
            key=lambda item: (
                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0.0,
                    )
                ),
                self._safe_float(
                    item.get(
                        "expected_value",
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

        values = self.value_bets(
            analyses
        )

        if not values:
            return None

        return max(
            values,
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

        total = len(
            analyses
        )

        values = self.value_bets(
            analyses
        )

        valid_items = [

            item

            for item in analyses

            if isinstance(
                item,
                dict,
            )
        ]

        if not valid_items:

            return {

                "total_analyses":
                    0,

                "total_value_bets":
                    0,

                "average_index":
                    0.0,

                "average_ev":
                    0.0,

                "best_opportunity":
                    None,

                "best_value_bet":
                    None,
            }

        indices = [

            self._safe_float(
                item.get(
                    "oddreal_index",
                    0.0,
                )
            )

            for item in valid_items
        ]

        evs = [

            self._safe_float(
                item.get(
                    "expected_value",
                    0.0,
                )
            )

            for item in valid_items
        ]

        average_index = (
            sum(indices)
            / len(indices)
            if indices
            else 0.0
        )

        average_ev = (
            sum(evs)
            / len(evs)
            if evs
            else 0.0
        )

        return {

            "total_analyses":
                total,

            "total_value_bets":
                len(values),

            "average_index":
                round(
                    average_index,
                    2,
                ),

            "average_ev":
                round(
                    average_ev,
                    3,
                ),

            "best_opportunity":
                self.best_opportunity(
                    analyses
                ),

            "best_value_bet":
                self.best_value_bet(
                    analyses
                ),
        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()


__all__ = [
    "Analyzer",
    "analyzer",
]

                
