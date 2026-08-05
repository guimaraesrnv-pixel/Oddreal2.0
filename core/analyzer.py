"""
OddReal 2.0
Core Analyzer

Motor central de análise quantitativa do OddReal.

Responsabilidades:
- filtrar bookmakers autorizados;
- normalizar nomes das casas;
- consolidar odds;
- calcular probabilidade implícita;
- remover overround por bookmaker;
- calcular consenso de mercado;
- identificar melhor odd disponível;
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
- NÃO utiliza Streamlit;
- NÃO altera bookmakers;
- trabalha somente com bookmakers autorizados.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config.bookmakers import (
    ALLOWED_BOOKMAKERS,
    normalize_bookmaker_name,
    bookmaker_display_name,
)

from modules.logger import info, error


class Analyzer:

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
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            result = float(
                value
            )

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

    @staticmethod
    def _safe_int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:
            return int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return default

    # ==========================================================
    # BOOKMAKERS
    # ==========================================================

    @staticmethod
    def _normalize_allowed_bookmaker(
        bookmaker: Any,
    ) -> Optional[str]:

        if bookmaker is None:
            return None

        normalized = (
            normalize_bookmaker_name(
                str(bookmaker)
            )
        )

        if normalized is None:
            return None

        if normalized not in (
            ALLOWED_BOOKMAKERS
        ):
            return None

        return normalized

    @staticmethod
    def _allowed_bookmaker(
        bookmaker: Any,
    ) -> bool:

        return (
            Analyzer
            ._normalize_allowed_bookmaker(
                bookmaker
            )
            is not None
        )

    @staticmethod
    def _normalized_bookmaker(
        bookmaker: Any,
    ) -> Optional[str]:

        return (
            Analyzer
            ._normalize_allowed_bookmaker(
                bookmaker
            )
        )

    @staticmethod
    def _display_bookmaker(
        bookmaker: Any,
    ) -> str:

        normalized = (
            Analyzer
            ._normalized_bookmaker(
                bookmaker
            )
        )

        if normalized is None:
            return "Casa não autorizada"

        return bookmaker_display_name(
            normalized
        )

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    def implied_probability(
        self,
        odd: float,
    ) -> float:

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return round(
            (
                1.0
                / odd
            )
            * 100.0,
            6,
        )

    # ==========================================================
    # OVERROUND
    # ==========================================================

    def calculate_overround(
        self,
        odds: List[float],
    ) -> float:

        probabilities = []

        for odd in odds:

            probability = (
                self.implied_probability(
                    odd
                )
            )

            if probability > 0.0:
                probabilities.append(
                    probability
                )

        if not probabilities:
            return 0.0

        return round(
            sum(probabilities)
            - 100.0,
            6,
        )

    # ==========================================================
    # REMOÇÃO DO OVERROUND
    # ==========================================================

    def remove_overround(
        self,
        probabilities: Dict[str, float],
    ) -> Dict[str, float]:

        if not isinstance(
            probabilities,
            dict,
        ):
            return {}

        valid = {}

        for (
            outcome,
            probability,
        ) in probabilities.items():

            value = (
                self._safe_float(
                    probability
                )
            )

            if value > 0.0:
                valid[
                    str(outcome)
                ] = value

        if not valid:
            return {}

        total = sum(
            valid.values()
        )

        if total <= 0.0:
            return {}

        normalized = {}

        for (
            outcome,
            probability,
        ) in valid.items():

            normalized[
                outcome
            ] = (
                probability
                / total
            ) * 100.0

        # Corrige pequenas diferenças
        # de arredondamento.
        total_normalized = sum(
            normalized.values()
        )

        if total_normalized <= 0.0:
            return {}

        normalized = {
            outcome: (
                probability
                / total_normalized
            ) * 100.0
            for (
                outcome,
                probability,
            )
            in normalized.items()
        }

        return {
            outcome: round(
                probability,
                6,
            )
            for (
                outcome,
                probability,
            )
            in normalized.items()
        }

    # ==========================================================
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:

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

        if (
            probability <= 0.0
            or odd <= 1.0
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
            6,
        )

    # ==========================================================
    # VALUE BET
    # ==========================================================

    def _is_value_bet(
        self,
        expected_value: float,
    ) -> bool:

        return (
            self._safe_float(
                expected_value
            )
            >= self.VALUE_BET_MIN_EV
        )

    @staticmethod
    def _value_classification(
        expected_value: float,
    ) -> str:

        ev = Analyzer._safe_float(
            expected_value
        )

        if ev >= 20.0:
            return "Excelente"

        if ev >= 15.0:
            return "Muito Forte"

        if ev >= 10.0:
            return "Forte"

        if ev >= 5.0:
            return "Value Bet"

        if ev > 0.0:
            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # RISCO
    # ==========================================================

    def _risk_level(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:

        odd = self._safe_float(
            odd
        )

        probability = self._safe_float(
            probability
        )

        index = self._safe_float(
            index
        )

        if probability < 15.0:
            return "Alto"

        if odd >= 8.0:
            return "Alto"

        if probability < 25.0:
            return "Alto"

        if odd >= 4.0:
            return "Moderado"

        if index < 45.0:
            return "Moderado"

        if index < 65.0:
            return "Moderado"

        return "Baixo"

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

        expected_value = (
            self._safe_float(
                expected_value
            )
        )

        market_count = max(
            0,
            self._safe_int(
                market_count
            ),
        )

        # ------------------------------------------------------
        # PROBABILIDADE
        # ------------------------------------------------------

        probability_score = min(
            45.0,
            probability * 0.45,
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        if expected_value > 0.0:

            ev_score = min(
                40.0,
                expected_value * 2.0,
            )

        else:

            ev_score = max(
                -30.0,
                expected_value * 1.5,
            )

        # ------------------------------------------------------
        # ROBUSTEZ
        # ------------------------------------------------------

        market_score = min(
            15.0,
            market_count * 3.0,
        )

        index = (
            probability_score
            + ev_score
            + market_score
        )

        # EV negativo nunca representa
        # oportunidade positiva.
        if expected_value < 0.0:
            index = min(
                index,
                25.0,
            )

        # Penalização de odds extremas.
        if odd >= 8.0:
            index *= 0.90

        return round(
            max(
                0.0,
                min(
                    100.0,
                    index,
                ),
            ),
            2,
        )

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
    # CHAVE INTERNA DO OUTCOME
    # ==========================================================

    @staticmethod
    def _outcome_key(
        outcome: Dict[str, Any],
    ) -> str:

        name = str(
            outcome.get(
                "name",
                ""
            )
        ).strip()

        if not name:
            return ""

        if "point" not in outcome:
            return name

        point = outcome.get(
            "point"
        )

        if point is None:
            return name

        try:
            point_value = float(
                point
            )

            if point_value.is_integer():
                point_text = str(
                    int(
                        point_value
                    )
                )
            else:
                point_text = str(
                    point_value
                )

        except (
            TypeError,
            ValueError,
        ):
            point_text = str(
                point
            ).strip()

        return (
            f"{name} {point_text}"
        ).strip()

    # ==========================================================
    # EXTRAÇÃO DE MERCADO
    # ==========================================================

    def _extract_market_data(
        self,
        event: Dict[str, Any],
    ) -> Dict[
        str,
        Dict[
            str,
            Dict[str, Any],
        ],
    ]:

        result: Dict[
            str,
            Dict[
                str,
                Dict[str, Any],
            ],
        ] = {}

        if not isinstance(
            event,
            dict,
        ):
            return result

        # ======================================================
        # FORMATO NOVO
        #
        # event
        #   bookmakers
        #       markets
        #           outcomes
        # ======================================================

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if isinstance(
            bookmakers,
            list,
        ):

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                # --------------------------------------------------
                # Primeiro tenta a chave normalizada criada pelo
                # DataManager.
                # --------------------------------------------------

                bookmaker_raw = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or bookmaker.get(
                        "key"
                    )
                    or bookmaker.get(
                        "title"
                    )
                )

                bookmaker_name = (
                    self._normalize_allowed_bookmaker(
                        bookmaker_raw
                    )
                )

                if bookmaker_name is None:
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
                            ""
                        )
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

                    for outcome in outcomes:

                        if not isinstance(
                            outcome,
                            dict,
                        ):
                            continue

                        outcome_name = str(
                            outcome.get(
                                "name",
                                ""
                            )
                        ).strip()

                        if not outcome_name:
                            continue

                        odd = self._safe_float(
                            outcome.get(
                                "price",
                                outcome.get(
                                    "odd",
                                    0.0,
                                ),
                            )
                        )

                        if odd <= 1.0:
                            continue

                        outcome_key = (
                            self._outcome_key(
                                outcome
                            )
                        )

                        if not outcome_key:
                            continue

                        result.setdefault(
                            market_key,
                            {},
                        )

                        result[
                            market_key
                        ].setdefault(
                            outcome_key,
                            {
                                "outcome_name":
                                    outcome_name,
                                "point":
                                    outcome.get(
                                        "point"
                                    ),
                                "odds": [],
                                "bookmakers": [],
                            },
                        )

                        data = result[
                            market_key
                        ][
                            outcome_key
                        ]

                        data[
                            "odds"
                        ].append(
                            odd
                        )

                        data[
                            "bookmakers"
                        ].append(
                            {
                                "name":
                                    bookmaker_name,
                                "normalized_name":
                                    bookmaker_name,
                                "display_name":
                                    bookmaker_display_name(
                                        bookmaker_name
                                    ),
                                "odd":
                                    odd,
                            }
                        )

        # ======================================================
        # FORMATO LEGADO
        #
        # Mantido apenas para compatibilidade.
        # ======================================================

        market_odds = event.get(
            "market_odds",
            [],
        )

        if isinstance(
            market_odds,
            list,
        ):

            for item in market_odds:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                market = str(
                    item.get(
                        "market",
                        item.get(
                            "market_key",
                            "",
                        ),
                    )
                ).strip()

                outcome = str(
                    item.get(
                        "outcome",
                        item.get(
                            "name",
                            item.get(
                                "outcome_name",
                                "",
                            ),
                        ),
                    )
                ).strip()

                bookmaker_raw = (
                    item.get(
                        "bookmaker",
                        item.get(
                            "bookmaker_key",
                            item.get(
                                "key",
                                "",
                            ),
                        ),
                    )
                )

                bookmaker_name = (
                    self._normalize_allowed_bookmaker(
                        bookmaker_raw
                    )
                )

                odd = self._safe_float(
                    item.get(
                        "odd",
                        item.get(
                            "price",
                            0.0,
                        ),
                    )
                )

                if (
                    not market
                    or not outcome
                    or bookmaker_name is None
                    or odd <= 1.0
                ):
                    continue

                point = item.get(
                    "point"
                )

                if point is not None:

                    try:
                        point_float = float(
                            point
                        )

                        if point_float.is_integer():
                            point_text = str(
                                int(
                                    point_float
                                )
                            )
                        else:
                            point_text = str(
                                point_float
                            )

                        outcome_key = (
                            f"{outcome} "
                            f"{point_text}"
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        outcome_key = outcome

                else:
                    outcome_key = outcome

                result.setdefault(
                    market,
                    {},
                )

                result[
                    market
                ].setdefault(
                    outcome_key,
                    {
                        "outcome_name":
                            outcome,
                        "point":
                            point,
                        "odds": [],
                        "bookmakers": [],
                    },
                )

                result[
                    market
                ][
                    outcome_key
                ][
                    "odds"
                ].append(
                    odd
                )

                result[
                    market
                ][
                    outcome_key
                ][
                    "bookmakers"
                ].append(
                    {
                        "name":
                            bookmaker_name,
                        "normalized_name":
                            bookmaker_name,
                        "display_name":
                            bookmaker_display_name(
                                bookmaker_name
                            ),
                        "odd":
                            odd,
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

        valid = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            name = (
                normalize_bookmaker_name(
                    bookmaker.get(
                        "normalized_name",
                        bookmaker.get(
                            "name",
                            "",
                        ),
                    )
                )
            )

            if name not in (
                ALLOWED_BOOKMAKERS
            ):
                continue

            odd = Analyzer._safe_float(
                bookmaker.get(
                    "odd",
                    0.0,
                )
            )

            if odd <= 1.0:
                continue

            item = dict(
                bookmaker
            )

            item[
                "name"
            ] = name

            item[
                "normalized_name"
            ] = name

            item[
                "display_name"
            ] = bookmaker_display_name(
                name
            )

            valid.append(
                item
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
            Dict[str, Any],
        ],
    ) -> Dict[str, float]:

        if not isinstance(
            outcomes,
            dict,
        ):
            return {}

        required_outcomes = set(
            outcomes.keys()
        )

        if not required_outcomes:
            return {}

        # bookmaker -> outcome -> odd
        bookmaker_odds: Dict[
            str,
            Dict[str, float],
        ] = {}

        for (
            outcome_key,
            data,
        ) in outcomes.items():

            if not isinstance(
                data,
                dict,
            ):
                continue

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

                bookmaker_name = (
                    self._normalize_allowed_bookmaker(
                        bookmaker.get(
                            "normalized_name",
                            bookmaker.get(
                                "name",
                                "",
                            ),
                        )
                    )
                )

                if bookmaker_name is None:
                    continue

                odd = self._safe_float(
                    bookmaker.get(
                        "odd",
                        0.0,
                    )
                )

                if odd <= 1.0:
                    continue

                bookmaker_odds.setdefault(
                    bookmaker_name,
                    {},
                )

                bookmaker_odds[
                    bookmaker_name
                ][
                    outcome_key
                ] = odd

        if not bookmaker_odds:
            return {}

        # ------------------------------------------------------
        # Fair probability por bookmaker
        # ------------------------------------------------------

        fair_distributions = []

        for (
            bookmaker_name,
            odds_by_outcome,
        ) in bookmaker_odds.items():

            # Uma casa só entra no consenso se possuir
            # TODAS as seleções daquela linha/mercado.
            if not required_outcomes.issubset(
                odds_by_outcome.keys()
            ):
                continue

            implied = {}

            valid_bookmaker = True

            for outcome_key in (
                required_outcomes
            ):

                odd = self._safe_float(
                    odds_by_outcome.get(
                        outcome_key,
                        0.0,
                    )
                )

                if odd <= 1.0:
                    valid_bookmaker = False
                    break

                implied[
                    outcome_key
                ] = self.implied_probability(
                    odd
                )

            if not valid_bookmaker:
                continue

            fair = (
                self.remove_overround(
                    implied
                )
            )

            if not fair:
                continue

            if not required_outcomes.issubset(
                fair.keys()
            ):
                continue

            fair_distributions.append(
                fair
            )

        if not fair_distributions:
            return {}

        # ------------------------------------------------------
        # Média das probabilidades justas
        # ------------------------------------------------------

        consensus = {}

        for outcome_key in (
            required_outcomes
        ):

            values = []

            for distribution in (
                fair_distributions
            ):

                if outcome_key in (
                    distribution
                ):
                    values.append(
                        self._safe_float(
                            distribution[
                                outcome_key
                            ]
                        )
                    )

            if values:
                consensus[
                    outcome_key
                ] = (
                    sum(values)
                    / len(values)
                )

        if not consensus:
            return {}

        # Normalização final.
        return self.remove_overround(
            consensus
        )

    # ==========================================================
    # VARIAÇÃO
    # ==========================================================

    @staticmethod
    def _variation(
        odds: List[float],
    ) -> float:

        if not isinstance(
            odds,
            list,
        ):
            return 0.0

        valid = []

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
            6,
        )

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

        analyses = []

        for event in events:

            try:

                analyses.extend(
                    self._analyze_event(
                        event
                    )
                )

            except Exception as exc:

                error(
                    "Erro ao analisar evento: "
                    f"{exc}"
                )

        info(
            f"{len(events)} eventos analisados."
        )

        info(
            f"{len(analyses)} análises "
            "quantitativas produzidas."
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
            event.get(
                "home",
                "Casa",
            ),
        )

        away_team = event.get(
            "away_team",
            event.get(
                "away",
                "Fora",
            ),
        )

        market_data = (
            self._extract_market_data(
                event
            )
        )

        results = []

        for (
            market,
            outcomes,
        ) in market_data.items():

            probabilities = (
                self._market_consensus(
                    outcomes
                )
            )

            if not probabilities:
                continue

            for (
                outcome_key,
                data,
            ) in outcomes.items():

                if not isinstance(
                    data,
                    dict,
                ):
                    continue

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

                probability = (
                    self._safe_float(
                        probabilities.get(
                            outcome_key,
                            0.0,
                        )
                    )
                )

                if (
                    best_odd <= 1.0
                    or probability <= 0.0
                ):
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
                # BOOKMAKERS AUTORIZADAS
                # ------------------------------------------------

                bookmaker_odds = []

                seen_bookmakers = set()

                for bookmaker in bookmakers:

                    if not isinstance(
                        bookmaker,
                        dict,
                    ):
                        continue

                    bookmaker_name = (
                        self._normalize_allowed_bookmaker(
                            bookmaker.get(
                                "normalized_name",
                                bookmaker.get(
                                    "name",
                                    "",
                                ),
                            )
                        )
                    )

                    if bookmaker_name is None:
                        continue

                    if bookmaker_name in (
                        seen_bookmakers
                    ):
                        continue

                    odd = self._safe_float(
                        bookmaker.get(
                            "odd",
                            0.0,
                        )
                    )

                    if odd <= 1.0:
                        continue

                    seen_bookmakers.add(
                        bookmaker_name
                    )

                    bookmaker_odds.append(
                        {
                            "name":
                                bookmaker_name,
                            "display_name":
                                bookmaker_display_name(
                                    bookmaker_name
                                ),
                            "odd":
                                round(
                                    odd,
                                    3,
                                ),
                        }
                    )

                if not bookmaker_odds:
                    continue

                # ------------------------------------------------
                # ÍNDICE
                # ------------------------------------------------

                market_count = len(
                    bookmaker_odds
                )

                oddreal_index = (
                    self._calculate_index(
                        probability=probability,
                        odd=best_odd,
                        expected_value=expected_value,
                        market_count=market_count,
                    )
                )

                # ------------------------------------------------
                # CLASSIFICAÇÕES
                # ------------------------------------------------

                confidence = (
                    self._confidence_level(
                        oddreal_index
                    )
                )

                risk = (
                    self._risk_level(
                        odd=best_odd,
                        probability=probability,
                        index=oddreal_index,
                    )
                )

                is_value = (
                    self._is_value_bet(
                        expected_value
                    )
                )

                value_classification = (
                    self._value_classification(
                        expected_value
                    )
                )

                # ------------------------------------------------
                # ODDS
                # ------------------------------------------------

                odds = [
                    item[
                        "odd"
                    ]
                    for item
                    in bookmaker_odds
                ]

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

                selected_bookmaker = (
                    self._display_bookmaker(
                        best_bookmaker.get(
                            "normalized_name",
                            best_bookmaker.get(
                                "name",
                                "",
                            ),
                        )
                    )
                )

                outcome_name = data.get(
                    "outcome_name",
                    outcome_key,
                )

                point = data.get(
                    "point"
                )

                # ------------------------------------------------
                # RESULTADO
                # ------------------------------------------------

                analysis = {

                    "event_id":
                        event_id,

                    "id":
                        event_id,

                    "sport_key":
                        event.get(
                            "sport_key"
                        ),

                    "sport_title":
                        event.get(
                            "sport_title"
                        ),

                    "home_team":
                        home_team,

                    "away_team":
                        away_team,

                    "commence_time":
                        event.get(
                            "commence_time"
                        ),

                    "market":
                        market,

                    "market_key":
                        market,

                    "selected_market":
                        market,

                    "outcome":
                        outcome_name,

                    "outcome_key":
                        outcome_key,

                    "selection":
                        outcome_name,

                    "selected_outcome":
                        outcome_name,

                    "point":
                        point,

                    "bookmaker":
                        selected_bookmaker,

                    "selected_bookmaker":
                        selected_bookmaker,

                    "bookmaker_display_name":
                        selected_bookmaker,

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
                        "fair_market_consensus",

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
                        value_classification,

                    "market_count":
                        market_count,

                    "available_bookmakers":
                        [
                            item[
                                "display_name"
                            ]
                            for item
                            in bookmaker_odds
                        ],

                    "bookmaker_odds":
                        bookmaker_odds,

                    "overround_considered":
                        True,

                    "analysis_scope":
                        "allowed_brazilian_bookmakers",
                }

                results.append(
                    analysis
                )

        return results

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

        values = []

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
            reverse=True,
        )

        info(
            f"{len(values)} Value Bets encontradas."
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

        positive = []

        for item in analyses:

            if not isinstance(
                item,
                dict,
            ):
                continue

            ev = self._safe_float(
                item.get(
                    "expected_value",
                    0.0,
                )
            )

            if ev <= 0.0:
                continue

            positive.append(
                item
            )

        if not positive:
            return None

        return max(
            positive,
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

        valid = [
            item
            for item in analyses
            if isinstance(
                item,
                dict,
            )
        ]

        values = self.value_bets(
            valid
        )

        if not valid:

            return {
                "total_analyses": 0,
                "total_value_bets": 0,
                "average_index": 0.0,
                "average_ev": 0.0,
                "best_opportunity": None,
                "best_value_bet": None,
                "allowed_bookmakers":
                    sorted(
                        ALLOWED_BOOKMAKERS
                    ),
            }

        indices = [
            self._safe_float(
                item.get(
                    "oddreal_index",
                    0.0,
                )
            )
            for item in valid
        ]

        evs = [
            self._safe_float(
                item.get(
                    "expected_value",
                    0.0,
                )
            )
            for item in valid
        ]

        return {

            "total_analyses":
                len(valid),

            "total_value_bets":
                len(values),

            "average_index":
                round(
                    sum(indices)
                    / len(indices),
                    2,
                )
                if indices
                else 0.0,

            "average_ev":
                round(
                    sum(evs)
                    / len(evs),
                    3,
                )
                if evs
                else 0.0,

            "best_opportunity":
                self.best_opportunity(
                    valid
                ),

            "best_value_bet":
                self.best_value_bet(
                    valid
                ),

            "allowed_bookmakers":
                sorted(
                    ALLOWED_BOOKMAKERS
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
  
