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

IMPORTANTE:
Este módulo trabalha diretamente com a estrutura normalizada
produzida pelo DataManager:

event
    └── bookmakers
          └── markets
                └── outcomes

Não espera mais um campo artificial "market_odds".
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
        info("Analyzer OddReal 2.0 iniciado.")

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Converte valor para float com segurança.
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

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(
        value: Any,
        default: int = 0,
    ) -> int:
        """
        Converte valor para int com segurança.
        """

        try:
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return default

    # ==========================================================
    # BOOKMAKERS
    # ==========================================================

    @staticmethod
    def _normalized_bookmaker(
        bookmaker: Any,
    ) -> str:
        """
        Normaliza o identificador do bookmaker.
        """

        return normalize_bookmaker_name(
            str(bookmaker or "").strip()
        )

    @classmethod
    def _allowed_bookmaker(
        cls,
        bookmaker: Any,
    ) -> bool:
        """
        Verifica se o bookmaker está autorizado.

        A comparação é feita de forma tolerante para evitar
        problemas quando ALLOWED_BOOKMAKERS contém nomes
        normalizados, títulos ou aliases.
        """

        normalized = cls._normalized_bookmaker(
            bookmaker
        )

        if not normalized:
            return False

        # ------------------------------------------------------
        # Normaliza a whitelist uma única vez.
        # ------------------------------------------------------

        normalized_allowed = set()

        try:
            for allowed in ALLOWED_BOOKMAKERS:

                normalized_allowed.add(
                    normalize_bookmaker_name(
                        str(
                            allowed
                        ).strip()
                    )
                )

        except Exception:
            return False

        return normalized in normalized_allowed

    @classmethod
    def _display_bookmaker(
        cls,
        bookmaker: Any,
    ) -> str:
        """
        Retorna nome amigável para exibição.
        """

        normalized = cls._normalized_bookmaker(
            bookmaker
        )

        if not normalized:
            return "Desconhecida"

        try:
            return bookmaker_display_name(
                normalized
            )

        except Exception:
            return normalized

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    def implied_probability(
        self,
        odd: float,
    ) -> float:
        """
        Probabilidade implícita:

            P = 1 / odd

        Retorno em percentual.
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return round(
            (
                1.0 / odd
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
        """
        Calcula o overround de um bookmaker.
        """

        probabilities = []

        if not isinstance(
            odds,
            list,
        ):
            return 0.0

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

        total = sum(
            probabilities
        )

        return round(
            total - 100.0,
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
        Remove a margem da casa.

        probabilidade justa =
        probabilidade implícita / soma das probabilidades.
        """

        if not isinstance(
            probabilities,
            dict,
        ):
            return {}

        valid = {}

        for outcome, probability in (
            probabilities.items()
        ):

            value = self._safe_float(
                probability
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

        for outcome, probability in (
            valid.items()
        ):

            normalized[
                outcome
            ] = (
                probability
                / total
            ) * 100.0

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
            for outcome, probability
            in normalized.items()
        }

        return {
            outcome: round(
                probability,
                6,
            )
            for outcome, probability
            in normalized.items()
        }

    # ==========================================================
    # EXPECTED VALUE
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        EV percentual.

            EV = (P × odd - 1) × 100

        probability é percentual.
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
        """
        Value Bet quando EV >= 5%.
        """

        return (
            self._safe_float(
                expected_value
            )
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
        Classificação descritiva de risco.

        O risco não altera o EV.
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

    def _risk(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:
        """
        Compatibilidade com chamadas antigas.
        """

        return self._risk_level(
            odd=odd,
            probability=probability,
            index=index,
        )

    # ==========================================================
    # CONFIANÇA
    # ==========================================================

    def _confidence_level(
        self,
        index: float,
    ) -> str:
        """
        Classificação baseada no Índice OddReal.
        """

        index = self._safe_float(
            index
        )

        if index >= 70.0:
            return "Alta"

        if index >= 45.0:
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # ÍNDICE ODDREAL
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

        Componentes:

        - probabilidade;
        - EV;
        - robustez de mercado.

        EV negativo nunca recebe bônus.
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
            self._safe_int(
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
        # ROBUSTEZ
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
        # EV NEGATIVO
        # ------------------------------------------------------

        if expected_value < 0.0:

            raw_index *= 0.60

        # ------------------------------------------------------
        # ODD MUITO ALTA
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

    def _oddreal_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int = 0,
    ) -> float:
        """
        Compatibilidade com chamadas antigas.
        """

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
            Dict[str, Any],
        ],
    ]:
        """
        Extrai mercados diretamente da estrutura normalizada
        utilizada pelo DataManager.

        Estrutura esperada:

        event
        └── bookmakers
            └── markets
                └── outcomes

        Exemplo:

        {
            "bookmakers": [
                {
                    "key": "bet365",
                    "title": "bet365",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {
                                    "name": "Time A",
                                    "price": 2.10
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        SOMENTE bookmakers autorizados participam.

        O método também aceita, por compatibilidade,
        eventos que eventualmente já possuam "market_odds".
        """

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
        # CAMINHO PRINCIPAL
        # Estrutura real da API:
        #
        # event -> bookmakers -> markets -> outcomes
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
                # Identificação da bookmaker
                # --------------------------------------------------

                raw_bookmaker = str(
                    bookmaker.get(
                        "key",
                        bookmaker.get(
                            "title",
                            bookmaker.get(
                                "name",
                                "",
                            ),
                        ),
                    )
                    or ""
                ).strip()

                if not raw_bookmaker:
                    continue

                normalized_bookmaker = (
                    self._normalized_bookmaker(
                        raw_bookmaker
                    )
                )

                # --------------------------------------------------
                # WHITELIST
                # --------------------------------------------------

                if normalized_bookmaker not in (
                    ALLOWED_BOOKMAKERS
                ):
                    continue

                display_name = (
                    self._display_bookmaker(
                        normalized_bookmaker
                    )
                )

                # --------------------------------------------------
                # Mercados
                # --------------------------------------------------

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
                            market.get(
                                "market",
                                "",
                            ),
                        )
                        or ""
                    ).strip()

                    if not market_key:
                        continue

                    # --------------------------------------------------
                    # Somente mercados primários
                    # --------------------------------------------------

                    if (
                        self.PRIMARY_MARKETS
                        and market_key
                        not in self.PRIMARY_MARKETS
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
                            or ""
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

                        # --------------------------------------------------
                        # Estrutura final
                        # --------------------------------------------------

                        result.setdefault(
                            market_key,
                            {},
                        )

                        result[
                            market_key
                        ].setdefault(
                            outcome_name,
                            {
                                "odds": [],
                                "bookmakers": [],
                            },
                        )

                        result[
                            market_key
                        ][
                            outcome_name
                        ][
                            "odds"
                        ].append(
                            odd
                        )

                        bookmaker_record = {
                            "name":
                                normalized_bookmaker,

                            "normalized_name":
                                normalized_bookmaker,

                            "display_name":
                                display_name,

                            "odd":
                                odd,
                        }

                        # --------------------------------------------------
                        # Ponto, quando existir
                        # --------------------------------------------------

                        if "point" in outcome:

                            point = self._safe_float(
                                outcome.get(
                                    "point"
                                ),
                                default=0.0,
                            )

                            if point != 0.0:

                                bookmaker_record[
                                    "point"
                                ] = point

                        result[
                            market_key
                        ][
                            outcome_name
                        ][
                            "bookmakers"
                        ].append(
                            bookmaker_record
                        )

        # ======================================================
        # COMPATIBILIDADE LEGADA
        #
        # Caso algum módulo ainda entregue:
        #
        # event["market_odds"]
        #
        # também aceitamos.
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
                    or ""
                ).strip()

                outcome = str(
                    item.get(
                        "outcome",
                        item.get(
                            "name",
                            "",
                        ),
                    )
                    or ""
                ).strip()

                raw_bookmaker = str(
                    item.get(
                        "bookmaker",
                        item.get(
                            "key",
                            "",
                        ),
                    )
                    or ""
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

                if not raw_bookmaker:
                    continue

                if odd <= 1.0:
                    continue

                normalized_bookmaker = (
                    self._normalized_bookmaker(
                        raw_bookmaker
                    )
                )

                if normalized_bookmaker not in (
                    ALLOWED_BOOKMAKERS
                ):
                    continue

                if (
                    self.PRIMARY_MARKETS
                    and market not in self.PRIMARY_MARKETS
                ):
                    continue

                display_name = (
                    self._display_bookmaker(
                        normalized_bookmaker
                    )
                )

                result.setdefault(
                    market,
                    {},
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
                        "name":
                            normalized_bookmaker,

                        "normalized_name":
                            normalized_bookmaker,

                        "display_name":
                            display_name,

                        "odd":
                            odd,
                    }
                )

        # ======================================================
        # REMOVER DUPLICATAS
        #
        # Pode existir duplicação caso um evento contenha
        # simultaneamente bookmakers e market_odds.
        # ======================================================

        for market, outcomes in result.items():

            for outcome_name, data in outcomes.items():

                bookmakers_data = data.get(
                    "bookmakers",
                    [],
                )

                unique_bookmakers = {}

                for bookmaker in bookmakers_data:

                    if not isinstance(
                        bookmaker,
                        dict,
                    ):
                        continue

                    bookmaker_name = str(
                        bookmaker.get(
                            "normalized_name",
                            bookmaker.get(
                                "name",
                                "",
                            ),
                        )
                        or ""
                    ).strip()

                    odd = self._safe_float(
                        bookmaker.get(
                            "odd",
                            0.0,
                        )
                    )

                    if (
                        not bookmaker_name
                        or odd <= 1.0
                    ):
                        continue

                    # Mantém a maior odd daquela bookmaker.
                    if (
                        bookmaker_name
                        not in unique_bookmakers
                        or odd
                        > self._safe_float(
                            unique_bookmakers[
                                bookmaker_name
                            ].get(
                                "odd",
                                0.0,
                            )
                        )
                    ):
                        unique_bookmakers[
                            bookmaker_name
                        ] = bookmaker

                cleaned_bookmakers = list(
                    unique_bookmakers.values()
                )

                data[
                    "bookmakers"
                ] = cleaned_bookmakers

                data[
                    "odds"
                ] = [
                    self._safe_float(
                        bookmaker.get(
                            "odd",
                            0.0,
                        )
                    )
                    for bookmaker
                    in cleaned_bookmakers
                    if self._safe_float(
                        bookmaker.get(
                            "odd",
                            0.0,
                        )
                    ) > 1.0
                ]

        return result

        # ======================================================
        # BOOKMAKERS
        # ======================================================

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            # --------------------------------------------------
            # O DataManager já pode ter produzido
            # _normalized_key.
            # --------------------------------------------------

            raw_key = (
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

            normalized_bookmaker = (
                self._normalized_bookmaker(
                    raw_key
                )
            )

            if not normalized_bookmaker:
                continue

            if not self._allowed_bookmaker(
                normalized_bookmaker
            ):
                continue

            display_name = (
                self._display_bookmaker(
                    normalized_bookmaker
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

            # ==================================================
            # MERCADOS
            # ==================================================

            for market in markets:

                if not isinstance(
                    market,
                    dict,
                ):
                    continue

                market_key = (
                    str(
                        market.get(
                            "key",
                            ""
                        )
                    ).strip()
                )

                if not market_key:
                    continue

                # ----------------------------------------------
                # Mercados suportados
                #
                # Não descartamos mercados adicionais.
                # O Analyzer pode analisar qualquer mercado
                # que possua outcomes válidos.
                # ----------------------------------------------

                outcomes = market.get(
                    "outcomes",
                    [],
                )

                if not isinstance(
                    outcomes,
                    list,
                ):
                    continue

                # ==================================================
                # OUTCOMES
                # ==================================================

                for outcome in outcomes:

                    if not isinstance(
                        outcome,
                        dict,
                    ):
                        continue

                    outcome_name = (
                        str(
                            outcome.get(
                                "name",
                                ""
                            )
                        ).strip()
                    )

                    if not outcome_name:
                        continue

                    odd = self._safe_float(
                        outcome.get(
                            "price",
                            0.0,
                        )
                    )

                    if odd <= 1.0:
                        continue

                    market_result = (
                        result.setdefault(
                            market_key,
                            {},
                        )
                    )

                    outcome_result = (
                        market_result.setdefault(
                            outcome_name,
                            {
                                "odds": [],
                                "bookmakers": [],
                            },
                        )
                    )

                    outcome_result[
                        "odds"
                    ].append(
                        odd
                    )

                    bookmaker_record = {
                        "name": (
                            normalized_bookmaker
                        ),
                        "normalized_name": (
                            normalized_bookmaker
                        ),
                        "display_name": (
                            display_name
                        ),
                        "odd": odd,
                    }

                    if "point" in outcome:

                        point = self._safe_float(
                            outcome.get(
                                "point"
                            ),
                            default=None,
                        )

                        if point is not None:

                            bookmaker_record[
                                "point"
                            ] = point

                    outcome_result[
                        "bookmakers"
                    ].append(
                        bookmaker_record
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
        """
        Retorna a maior odd disponível.
        """

        if not isinstance(
            bookmakers,
            list,
        ):
            return None

        valid = []

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

            if odd <= 1.0:
                continue

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
            Dict[str, Any],
        ],
    ) -> Dict[str, float]:
        """
        Calcula a probabilidade justa de mercado.

        Processo:

        1. separa odds por bookmaker;
        2. exige todas as seleções do mercado;
        3. calcula probabilidade implícita;
        4. remove overround;
        5. calcula consenso entre bookmakers;
        6. normaliza para 100%.
        """

        if not isinstance(
            outcomes,
            dict,
        ):
            return {}

        required_outcomes = {
            str(
                outcome
            )
            for outcome in outcomes.keys()
        }

        if not required_outcomes:
            return {}

        # ======================================================
        # bookmaker -> outcome -> odd
        # ======================================================

        bookmaker_odds = {}

        for outcome_name, data in (
            outcomes.items()
        ):

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
                    bookmaker.get(
                        "normalized_name"
                    )
                    or bookmaker.get(
                        "name"
                    )
                    or bookmaker.get(
                        "key"
                    )
                )

                bookmaker_name = (
                    self._normalized_bookmaker(
                        bookmaker_name
                    )
                )

                if not bookmaker_name:
                    continue

                if not self._allowed_bookmaker(
                    bookmaker_name
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

                bookmaker_odds.setdefault(
                    bookmaker_name,
                    {},
                )

                bookmaker_odds[
                    bookmaker_name
                ][
                    str(outcome_name)
                ] = odd

        if not bookmaker_odds:
            return {}

        # ======================================================
        # PROBABILIDADE JUSTA POR BOOKMAKER
        # ======================================================

        normalized_probabilities = {}

        for (
            bookmaker_name,
            odds_by_outcome,
        ) in bookmaker_odds.items():

            # Uma casa precisa possuir todas as seleções.
            if not required_outcomes.issubset(
                set(
                    odds_by_outcome.keys()
                )
            ):
                continue

            implied = {}

            valid_bookmaker = True

            for outcome_name in (
                required_outcomes
            ):

                odd = self._safe_float(
                    odds_by_outcome.get(
                        outcome_name,
                        0.0,
                    )
                )

                if odd <= 1.0:

                    valid_bookmaker = False
                    break

                implied[
                    outcome_name
                ] = (
                    self.implied_probability(
                        odd
                    )
                )

            if not valid_bookmaker:
                continue

            if not implied:
                continue

            fair = (
                self.remove_overround(
                    implied
                )
            )

            if not fair:
                continue

            normalized_probabilities[
                bookmaker_name
            ] = fair

        if not normalized_probabilities:
            return {}

        # ======================================================
        # CONSENSO
        # ======================================================

        consensus_values = {}

        for outcome_name in (
            required_outcomes
        ):

            values = []

            for fair_distribution in (
                normalized_probabilities.values()
            ):

                if (
                    outcome_name
                    not in fair_distribution
                ):
                    continue

                values.append(
                    self._safe_float(
                        fair_distribution[
                            outcome_name
                        ]
                    )
                )

            if values:

                consensus_values[
                    outcome_name
                ] = (
                    sum(values)
                    / len(values)
                )

        if not consensus_values:
            return {}

        # ======================================================
        # NORMALIZAÇÃO FINAL
        # ======================================================

        total = sum(
            consensus_values.values()
        )

        if total <= 0.0:
            return {}

        return {
            outcome: round(
                (
                    probability
                    / total
                )
                * 100.0,
                6,
            )
            for outcome, probability
            in consensus_values.items()
        }

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
        """
        Analisa todos os eventos recebidos.
        """

        if not isinstance(
            events,
            list,
        ):
            return []

        analyses = []

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
        """
        Analisa um único evento.
        """

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

        if not market_data:

            info(
                f"Evento {event_id} não possui "
                "mercados autorizados utilizáveis."
            )

            return []

        results = []

        # ======================================================
        # MERCADOS
        # ======================================================

        for market, outcomes in (
            market_data.items()
        ):

            probabilities = (
                self._market_consensus(
                    outcomes
                )
            )

            if not probabilities:
                continue

            # ==================================================
            # SELEÇÕES
            # ==================================================

            for outcome_name, data in (
                outcomes.items()
            ):

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

                # ==============================================
                # MELHOR CASA
                # ==============================================

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

                # ==============================================
                # PROBABILIDADE JUSTA
                # ==============================================

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

                # ==============================================
                # EV
                # ==============================================

                expected_value = (
                    self.expected_value(
                        probability=probability,
                        odd=best_odd,
                    )
                )

                # ==============================================
                # CONTAGEM DE CASAS
                # ==============================================

                allowed_bookmakers = []

                for bookmaker in bookmakers:

                    if not isinstance(
                        bookmaker,
                        dict,
                    ):
                        continue

                    name = (
                        bookmaker.get(
                            "normalized_name"
                        )
                        or bookmaker.get(
                            "name"
                        )
                        or bookmaker.get(
                            "key"
                        )
                    )

                    name = (
                        self._normalized_bookmaker(
                            name
                        )
                    )

                    if not self._allowed_bookmaker(
                        name
                    ):
                        continue

                    allowed_bookmakers.append(
                        name
                    )

                allowed_bookmakers = list(
                    dict.fromkeys(
                        allowed_bookmakers
                    )
                )

                market_count = len(
                    allowed_bookmakers
                )

                # ==============================================
                # ÍNDICE
                # ==============================================

                oddreal_index = (
                    self._calculate_index(
                        probability=probability,
                        odd=best_odd,
                        expected_value=expected_value,
                        market_count=market_count,
                    )
                )

                # ==============================================
                # CONFIANÇA
                # ==============================================

                confidence = (
                    self._confidence_level(
                        oddreal_index
                    )
                )

                # ==============================================
                # RISCO
                # ==============================================

                risk = (
                    self._risk_level(
                        odd=best_odd,
                        probability=probability,
                        index=oddreal_index,
                    )
                )

                # ==============================================
                # VALUE BET
                # ==============================================

                is_value = (
                    self._is_value_bet(
                        expected_value
                    )
                )

                # ==============================================
                # ODDS
                # ==============================================

                odds = data.get(
                    "odds",
                    [],
                )

                if not isinstance(
                    odds,
                    list,
                ):
                    odds = []

                valid_odds = []

                for odd in odds:

                    value = (
                        self._safe_float(
                            odd
                        )
                    )

                    if value > 1.0:
                        valid_odds.append(
                            value
                        )

                average_odd = (
                    sum(valid_odds)
                    / len(valid_odds)
                    if valid_odds
                    else 0.0
                )

                variation = (
                    self._variation(
                        valid_odds
                    )
                )

                # ==============================================
                # BOOKMAKERS DISPONÍVEIS
                # ==============================================

                available_bookmakers = []

                bookmaker_odds = {}

                for bookmaker in bookmakers:

                    if not isinstance(
                        bookmaker,
                        dict,
                    ):
                        continue

                    normalized_name = (
                        bookmaker.get(
                            "normalized_name"
                        )
                        or bookmaker.get(
                            "name"
                        )
                        or bookmaker.get(
                            "key"
                        )
                    )

                    normalized_name = (
                        self._normalized_bookmaker(
                            normalized_name
                        )
                    )

                    if not self._allowed_bookmaker(
                        normalized_name
                    ):
                        continue

                    odd = (
                        self._safe_float(
                            bookmaker.get(
                                "odd",
                                0.0,
                            )
                        )
                    )

                    if odd <= 1.0:
                        continue

                    display_name = (
                        self._display_bookmaker(
                            normalized_name
                        )
                    )

                    available_bookmakers.append(
                        display_name
                    )

                    bookmaker_odds[
                        display_name
                    ] = round(
                        odd,
                        3,
                    )

                available_bookmakers = list(
                    dict.fromkeys(
                        available_bookmakers
                    )
                )

                # ==============================================
                # MELHOR BOOKMAKER
                # ==============================================

                selected_bookmaker = (
                    best_bookmaker.get(
                        "display_name"
                    )
                    or best_bookmaker.get(
                        "normalized_name"
                    )
                    or best_bookmaker.get(
                        "name"
                    )
                )

                selected_bookmaker = (
                    self._display_bookmaker(
                        selected_bookmaker
                    )
                )

                # ==============================================
                # RESULTADO
                # ==============================================

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
                            "sport_title",
                            event.get(
                                "sport_key"
                            ),
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

                    "selected_market":
                        market,

                    "market_key":
                        market,

                    "outcome":
                        outcome_name,

                    "selection":
                        outcome_name,

                    "selected_outcome":
                        outcome_name,

                    "bookmaker":
                        selected_bookmaker,

                    "selected_bookmaker":
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
                        (
                            "Value Bet"
                            if is_value
                            else (
                                "Positivo"
                                if expected_value > 0.0
                                else "Sem Valor"
                            )
                        ),

                    "market_count":
                        market_count,

                    "available_bookmakers":
                        available_bookmakers,

                    "bookmaker_odds":
                        bookmaker_odds,

                    "overround_considered":
                        True,

                    "analysis_scope":
                        "allowed_brazilian_bookmakers",

                }

                # Preserva point quando existir.
                if "point" in best_bookmaker:

                    point = (
                        self._safe_float(
                            best_bookmaker.get(
                                "point"
                            ),
                            default=None,
                        )
                    )

                    if point is not None:

                        analysis[
                            "point"
                        ] = point

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
        """
        Variação percentual entre menor
        e maior odd.

            ((máxima - mínima) / mínima) × 100
        """

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
        Retorna análises com EV >= 5%.
        """

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
        """
        Melhor oportunidade:

        1. EV positivo;
        2. maior EV;
        3. maior Índice OddReal;
        4. maior probabilidade.
        """

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
        """
        Retorna a Value Bet com maior EV.
        """

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
        """
        Gera resumo estatístico.
        """

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

        allowed_bookmakers = sorted(
            str(
                bookmaker
            )
            for bookmaker
            in ALLOWED_BOOKMAKERS
        )

        if not valid:

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

                "allowed_bookmakers":
                    allowed_bookmakers,

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
                len(valid),

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
                    valid
                ),

            "best_value_bet":
                self.best_value_bet(
                    valid
                ),

            "allowed_bookmakers":
                allowed_bookmakers,

        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()


__all__ = [
    "Analyzer",
    "analyzer",
]
                       
