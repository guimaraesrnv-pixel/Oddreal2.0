"""
OddReal 2.0
Analyzer

Motor central de análise quantitativa.

Responsável por:

- utilizar somente bookmakers autorizados;
- consolidar odds;
- calcular probabilidade implícita;
- remover overround individualmente por bookmaker;
- calcular consenso de mercado;
- encontrar melhor odd;
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
- NÃO depende do Streamlit;
- NÃO altera bookmakers;
- NÃO utiliza casas fora da whitelist.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error

from config.bookmakers import (
    ALLOWED_BOOKMAKERS,
    normalize_bookmaker_name,
    bookmaker_display_name,
)


class Analyzer:
    """
    Motor quantitativo principal do OddReal.
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

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return round(
            (1.0 / odd) * 100.0,
            6,
        )

    # ==========================================================
    # REMOÇÃO DO OVERROUND
    # ==========================================================

    def remove_overround(
        self,
        probabilities: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Remove a margem matemática da casa.

        Exemplo:

            A = 50%
            B = 30%
            C = 25%

        Soma = 105%

        Normalização:

            A = 47.619%
            B = 28.571%
            C = 23.810%

        O resultado soma 100%.
        """

        valid = {
            name: self._safe_float(
                probability
            )
            for name, probability
            in probabilities.items()
            if self._safe_float(
                probability
            ) > 0.0
        }

        total = sum(
            valid.values()
        )

        if total <= 0.0:
            return {}

        return {
            name: round(
                (
                    probability
                    / total
                )
                * 100.0,
                6,
            )
            for name, probability
            in valid.items()
        }

    # ==========================================================
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        EV percentual.

        EV =
            ((P / 100) × odd - 1) × 100
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

    # ==========================================================
    # CLASSIFICAÇÃO DE VALUE
    # ==========================================================

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

    # Compatibilidade
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
        Índice de qualidade da oportunidade.

        Componentes:

        - probabilidade;
        - EV;
        - quantidade de bookmakers;
        - penalização de EV negativo.

        O índice NÃO substitui o EV.
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

        # Probabilidade:
        probability_score = min(
            45.0,
            probability * 0.45,
        )

        # EV:
        if expected_value > 0.0:

            ev_score = min(
                40.0,
                expected_value * 2.0,
            )

        else:

            # EV negativo penaliza fortemente.
            ev_score = max(
                -30.0,
                expected_value * 1.5,
            )

        # Robustez:
        market_score = min(
            15.0,
            market_count * 3.0,
        )

        index = (
            probability_score
            + ev_score
            + market_score
        )

        # EV negativo não pode resultar
        # em índice de oportunidade.
        if expected_value < 0.0:

            index = min(
                index,
                25.0,
            )

        # Odds extremamente altas recebem
        # pequena penalização de robustez.
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

    # Compatibilidade
    def _oddreal_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int = 0,
    ) -> float:

        return self._calculate_index(
            probability,
            odd,
            expected_value,
            market_count,
        )

    # ==========================================================
    # BOOKMAKER
    # ==========================================================

    @staticmethod
    def _normalize_allowed_bookmaker(
        bookmaker: Any,
    ) -> Optional[str]:

        normalized = normalize_bookmaker_name(
            bookmaker
        )

        if normalized is None:
            return None

        if normalized not in ALLOWED_BOOKMAKERS:
            return None

        return normalized

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
            Dict[str, Any]
        ]
    ]:
        """
        Extrai somente bookmakers autorizados.
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

            bookmaker_raw = item.get(
                "bookmaker",
                item.get(
                    "bookmaker_title",
                    "",
                ),
            )

            bookmaker = (
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

            # --------------------------------------------------
            # FILTROS
            # --------------------------------------------------

            if not market:
                continue

            if not outcome:
                continue

            if bookmaker is None:
                continue

            if odd <= 1.0:
                continue

            # --------------------------------------------------
            # ESTRUTURA
            # --------------------------------------------------

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
                    "display_name":
                        bookmaker_display_name(
                            bookmaker
                        ),
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

        valid = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            name = normalize_bookmaker_name(
                bookmaker.get(
                    "name",
                    "",
                )
            )

            if name not in ALLOWED_BOOKMAKERS:
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

            item["name"] = name

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
    # CONSENSO POR BOOKMAKER
    # ==========================================================

    def _market_consensus(
        self,
        outcomes: Dict[
            str,
            Dict[str, Any]
        ],
    ) -> Dict[str, float]:
        """
        Calcula o consenso de mercado.

        Para cada bookmaker autorizado:

        1. pega todas as seleções disponíveis;
        2. transforma odds em probabilidades implícitas;
        3. remove o overround;
        4. gera uma distribuição de 100%.

        Depois:

        5. calcula a média das probabilidades
           normalizadas.

        Bookmakers que não possuem todas as seleções
        necessárias são ignorados para evitar distribuições
        incompletas contaminando o consenso.
        """

        bookmaker_data: Dict[
            str,
            Dict[str, float]
        ] = {}

        required_outcomes = set(
            outcomes.keys()
        )

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

                bookmaker_name = (
                    self._normalize_allowed_bookmaker(
                        bookmaker.get(
                            "name",
                            "",
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

                bookmaker_data.setdefault(
                    bookmaker_name,
                    {}
                )

                bookmaker_data[
                    bookmaker_name
                ][
                    outcome_name
                ] = self.implied_probability(
                    odd
                )

        # ------------------------------------------------------
        # NORMALIZA CADA BOOKMAKER
        # ------------------------------------------------------

        normalized_distributions: List[
            Dict[str, float]
        ] = []

        for (
            bookmaker_name,
            probabilities,
        ) in bookmaker_data.items():

            # Para o mercado principal, só usamos uma casa
            # quando ela possui todas as seleções.
            if required_outcomes:
                if not required_outcomes.issubset(
                    probabilities.keys()
                ):
                    continue

            normalized = (
                self.remove_overround(
                    probabilities
                )
            )

            if not normalized:
                continue

            if not required_outcomes.issubset(
                normalized.keys()
            ):
                continue

            normalized_distributions.append(
                normalized
            )

        if not normalized_distributions:
            return {}

        # ------------------------------------------------------
        # MÉDIA DAS DISTRIBUIÇÕES
        # ------------------------------------------------------

        consensus: Dict[
            str,
            float
        ] = {}

        for outcome_name in required_outcomes:

            values = [

                distribution[
                    outcome_name
                ]

                for distribution
                in normalized_distributions

                if outcome_name
                in distribution
            ]

            if not values:
                continue

            consensus[
                outcome_name
            ] = (
                sum(values)
                / len(values)
            )

        # ------------------------------------------------------
        # NORMALIZAÇÃO FINAL
        # ------------------------------------------------------

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
            4,
        )

    # ==========================================================
    # ANALYZE
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
            f"{len(analyses)} análises "
            "quantitativas produzidas."
        )

        return analyses

    # ==========================================================
    # ANALYZE EVENT
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

        results = []

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
            # CADA SELEÇÃO
            # --------------------------------------------------

            for (
                outcome_name,
                data,
            ) in outcomes.items():

                bookmakers = data.get(
                    "bookmakers",
                    [],
                )

                if not bookmakers:
                    continue

                best_bookmaker = (
                    self._best_bookmaker(
                        bookmakers
                    )
                )

                if best_bookmaker is None:
                    continue

                best_odd = self._safe_float(
                    best_bookmaker.get(
                        "odd",
                        0.0,
                    )
                )

                probability = (
                    self._safe_float(
                        probabilities.get(
                            outcome_name,
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
                # ÍNDICE
                # ------------------------------------------------

                oddreal_index = (
                    self._calculate_index(
                        probability=probability,
                        odd=best_odd,
                        expected_value=expected_value,
                        market_count=len(
                            {
                                normalize_bookmaker_name(
                                    b.get(
                                        "name",
                                        "",
                                    )
                                )
                                for b in bookmakers
                                if isinstance(
                                    b,
                                    dict,
                                )
                                and normalize_bookmaker_name(
                                    b.get(
                                        "name",
                                        "",
                                    )
                                )
                                in ALLOWED_BOOKMAKERS
                            }
                        ),
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
                # TODAS AS ODDS AUTORIZADAS
                # ------------------------------------------------

                bookmaker_odds = []

                for bookmaker in bookmakers:

                    if not isinstance(
                        bookmaker,
                        dict,
                    ):
                        continue

                    bookmaker_name = (
                        normalize_bookmaker_name(
                            bookmaker.get(
                                "name",
                                "",
                            )
                        )
                    )

                    if bookmaker_name not in (
                        ALLOWED_BOOKMAKERS
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

                odds = [
                    item["odd"]
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
                            "",
                        ),

                    "bookmaker_display_name":
                        best_bookmaker.get(
                            "display_name",
                            bookmaker_display_name(
                                best_bookmaker.get(
                                    "name",
                                    "",
                                )
                            ),
                        ),

                    "selected_bookmaker":
                        best_bookmaker.get(
                            "name",
                            "",
                        ),

                    "selected_bookmaker_display_name":
                        best_bookmaker.get(
                            "display_name",
                            "",
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
                        "authorized_bookmaker_consensus",

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
                        len(
                            bookmaker_odds
                        ),

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

    # ------------------------------------------------------
    # SOMENTE ANÁLISES VÁLIDAS
    # ------------------------------------------------------

    positive = [
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
            ) > 0.0
        )
    ]

    # Nenhuma oportunidade com EV positivo
    if not positive:
        return None

    # ------------------------------------------------------
    # MELHOR OPORTUNIDADE
    # ------------------------------------------------------
    #
    # Prioridade:
    #
    # 1. EV
    # 2. Índice OddReal
    # 3. Probabilidade
    #
    # Assim o sistema não escolhe uma odd
    # simplesmente por ser mais alta.
    # ------------------------------------------------------

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
            Dict[str, Any
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

        if len(valid) < 2:
            return 0.0

        minimum = min(
     
                
