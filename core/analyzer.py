"""
OddReal 2.0
Analyzer

Arquivo:
core/analyzer.py

Responsável por:

- Analisar eventos preparados pelo Pipeline;
- Selecionar a melhor cotação disponível por seleção;
- Construir uma referência estatística do mercado;
- Calcular probabilidade implícita;
- Calcular probabilidade de consenso;
- Remover a margem do mercado;
- Calcular EV;
- Calcular variação de mercado;
- Calcular Índice OddReal;
- Classificar risco e confiança;
- Integrar o ValueBetEngine;
- Identificar oportunidades;
- Gerar resumo das análises.

IMPORTANTE:

O Analyzer não consulta a API.

A probabilidade utilizada no EV não é simplesmente
a probabilidade implícita da própria odd.

O cálculo utiliza as demais cotações disponíveis
para construir uma referência de mercado.

A IA permanece exclusivamente na camada interpretativa.
"""

from __future__ import annotations

from statistics import median
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
        Converte um valor para float com segurança.
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
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:
        """
        Converte um valor para string com segurança.
        """

        if value is None:
            return default

        value = str(value).strip()

        return value or default

    # ==========================================================
    # EXTRAÇÃO DE TODAS AS COTAÇÕES
    # ==========================================================

    def _extract_market_prices(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extrai todas as cotações agrupadas por seleção.

        Estrutura retornada:

        {
            "Mandante": [
                {
                    "odd": 2.10,
                    "bookmaker": "..."
                }
            ],
            "Draw": [
                ...
            ],
            "Visitante": [
                ...
            ]
        }

        O agrupamento é feito pela seleção.
        """

        grouped: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):
            return grouped

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            bookmaker_name = self._safe_string(
                bookmaker.get(
                    "title",
                    bookmaker.get(
                        "name",
                        bookmaker.get(
                            "key",
                            "",
                        ),
                    ),
                ),
                "Casa não informada",
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

                market_key = self._safe_string(
                    market.get(
                        "key",
                        "",
                    ),
                    "Mercado",
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

                    outcome_name = self._safe_string(
                        outcome.get(
                            "name",
                            "",
                        )
                    )

                    odd = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if not outcome_name:
                        continue

                    if odd <= 1.0:
                        continue

                    grouped.setdefault(
                        outcome_name,
                        [],
                    ).append(
                        {
                            "odd": odd,
                            "bookmaker": bookmaker_name,
                            "market": market_key,
                        }
                    )

        return grouped

    # ==========================================================
    # MELHOR COTAÇÃO POR SELEÇÃO
    # ==========================================================

    def _get_best_odd_for_outcome(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna a maior cotação disponível para uma
        determinada seleção.
        """

        grouped = self._extract_market_prices(
            event
        )

        prices = grouped.get(
            selected_outcome,
            [],
        )

        if not prices:
            return None

        best = max(
            prices,
            key=lambda item:
                self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                ),
        )

        return {
            "odd": self._safe_float(
                best.get(
                    "odd",
                    0,
                )
            ),
            "bookmaker": self._safe_string(
                best.get(
                    "bookmaker",
                    "",
                )
            ),
            "market": self._safe_string(
                best.get(
                    "market",
                    "",
                )
            ),
            "outcome": selected_outcome,
        }

    # ==========================================================
    # TODAS AS SELEÇÕES
    # ==========================================================

    def _get_market_outcomes(
        self,
        event: Dict[str, Any],
    ) -> List[str]:
        """
        Retorna todas as seleções encontradas no mercado.
        """

        grouped = self._extract_market_prices(
            event
        )

        return list(
            grouped.keys()
        )

    # ==========================================================
    # MELHOR ODD
    # ==========================================================

    def _get_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Seleciona a maior cotação disponível no evento.

        Se best_odd já tiver sido produzido pelo Pipeline,
        ele é respeitado quando estiver válido.

        Caso contrário, procura diretamente nas casas.
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

            outcome = self._safe_string(
                existing.get(
                    "outcome",
                    "",
                )
            )

            if (
                odd > 1.0
                and outcome
            ):

                return {
                    "odd": odd,
                    "bookmaker":
                        self._safe_string(
                            existing.get(
                                "bookmaker",
                                "",
                            )
                        ),
                    "market":
                        self._safe_string(
                            existing.get(
                                "market",
                                "",
                            )
                        ),
                    "outcome": outcome,
                }

        grouped = self._extract_market_prices(
            event
        )

        candidates: List[
            Dict[str, Any]
        ] = []

        for outcome, prices in grouped.items():

            for item in prices:

                odd = self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                )

                if odd <= 1.0:
                    continue

                candidates.append(
                    {
                        "odd": odd,
                        "bookmaker":
                            self._safe_string(
                                item.get(
                                    "bookmaker",
                                    "",
                                )
                            ),
                        "market":
                            self._safe_string(
                                item.get(
                                    "market",
                                    "",
                                )
                            ),
                        "outcome": outcome,
                    }
                )

        if not candidates:
            return None

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
    # MEDIANA DA COTAÇÃO
    # ==========================================================

    def _calculate_outcome_median(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
    ) -> float:
        """
        Calcula a mediana das cotações daquela seleção.

        A mediana é utilizada em vez da média para reduzir
        o impacto de uma cotação isolada muito distante
        do restante do mercado.
        """

        grouped = self._extract_market_prices(
            event
        )

        prices = [

            self._safe_float(
                item.get(
                    "odd",
                    0,
                )
            )

            for item in grouped.get(
                selected_outcome,
                [],
            )

            if self._safe_float(
                item.get(
                    "odd",
                    0,
                )
            ) > 1.0
        ]

        if not prices:
            return 0.0

        return round(
            float(
                median(prices)
            ),
            4,
        )

    # ==========================================================
    # REFERÊNCIA DE MERCADO
    # ==========================================================

    def _calculate_market_reference(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Constrói uma referência estatística para cada seleção.

        Para cada resultado:

        1. coleta todas as odds;
        2. calcula a mediana;
        3. converte para probabilidade implícita;
        4. remove a margem do mercado;
        5. gera uma probabilidade de referência.

        Retorno:

        {
            "Seleção": {
                "median_odd": ...,
                "implied_probability": ...,
                "fair_probability": ...,
                "sources": ...
            }
        }
        """

        grouped = self._extract_market_prices(
            event
        )

        if not grouped:
            return {}

        raw_probabilities: Dict[
            str,
            float
        ] = {}

        references: Dict[
            str,
            Dict[str, Any]
        ] = {}

        # ------------------------------------------------------
        # MEDIANA + PROBABILIDADE IMPLÍCITA
        # ------------------------------------------------------

        for outcome, prices in grouped.items():

            valid_prices = [

                self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                )

                for item in prices

                if self._safe_float(
                    item.get(
                        "odd",
                        0,
                    )
                ) > 1.0
            ]

            if not valid_prices:
                continue

            median_odd = float(
                median(valid_prices)
            )

            implied_probability = (
                1.0 / median_odd
            )

            raw_probabilities[
                outcome
            ] = implied_probability

            references[
                outcome
            ] = {
                "median_odd":
                    round(
                        median_odd,
                        4,
                    ),
                "implied_probability":
                    round(
                        implied_probability
                        * 100.0,
                        4,
                    ),
                "sources":
                    len(valid_prices),
            }

        if not raw_probabilities:
            return {}

        # ------------------------------------------------------
        # REMOÇÃO DA MARGEM
        # ------------------------------------------------------

        total_probability = sum(
            raw_probabilities.values()
        )

        if total_probability <= 0:
            return {}

        for outcome, raw_probability in (
            raw_probabilities.items()
        ):

            fair_probability = (
                raw_probability
                / total_probability
            )

            references[
                outcome
            ][
                "fair_probability"
            ] = round(
                fair_probability
                * 100.0,
                4,
            )

        return references

    # ==========================================================
    # PROBABILIDADE JUSTA
    # ==========================================================

    def _calculate_fair_probability(
        self,
        event: Dict[str, Any],
        selected_outcome: str,
    ) -> float:
        """
        Retorna a probabilidade de referência da seleção.
        """

        reference = (
            self._calculate_market_reference(
                event
            )
        )

        selected = reference.get(
            selected_outcome,
            {},
        )

        return self._safe_float(
            selected.get(
                "fair_probability",
                0,
            )
        )

    # ==========================================================
    # EV
    # ==========================================================

    @staticmethod
    def _calculate_expected_value(
        fair_probability: float,
        odd: float,
    ) -> float:
        """
        Calcula EV percentual.

        fair_probability:
            escala 0-100.

        Fórmula:

            EV = ((p / 100) × odd - 1) × 100
        """

        probability = (
            fair_probability
            / 100.0
        )

        if (
            probability <= 0
            or odd <= 0
        ):
            return 0.0

        return (
            (
                probability
                * odd
            )
            - 1.0
        ) * 100.0

    # ==========================================================
    # VARIAÇÃO DA ODD
    # ==========================================================

    @staticmethod
    def _market_variation(
        odd: float,
        reference_odd: float,
    ) -> float:
        """
        Mede a diferença percentual entre a cotação
        selecionada e a referência de mercado.
        """

        if reference_odd <= 0:
            return 0.0

        return round(
            (
                (
                    odd
                    - reference_odd
                )
                / reference_odd
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
        sources: int,
    ) -> str:
        """
        Classificação de risco baseada na qualidade
        da informação disponível.

        Não representa garantia de resultado.
        """

        if sources < 2:
            return "Alto"

        if variation > 50:
            return "Alto"

        if probability >= 65 and expected_value >= 8:
            return "Moderado"

        if probability >= 50 and expected_value >= 5:
            return "Moderado"

        return "Alto"

    # ==========================================================
    # CONFIANÇA
    # ==========================================================

    @staticmethod
    def _confidence_level(
        index: int,
        sources: int,
    ) -> str:
        """
        Classifica a confiança do indicador.
        """

        if sources < 2:
            return "Baixa"

        if (
            index >= 80
            and sources >= 5
        ):
            return "Muito Alta"

        if (
            index >= 70
            and sources >= 4
        ):
            return "Alta"

        if (
            index >= 55
            and sources >= 3
        ):
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # ÍNDICE ODREAL
    # ==========================================================

    @staticmethod
    def _calculate_oddreal_index(
        probability: float,
        expected_value: float,
        market_variation: float,
        sources: int,
    ) -> int:
        """
        Calcula o Índice OddReal de 0 a 100.

        Componentes:

        - probabilidade de referência;
        - EV;
        - diferença em relação ao mercado;
        - quantidade de fontes.

        Uma cotação isolada não recebe pontuação máxima
        de confiança.
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

        variation_score = min(
            max(
                50.0
                + (
                    market_variation
                    * 1.5
                ),
                0.0,
            ),
            100.0,
        )

        source_score = min(
            max(
                sources
                * 15.0,
                0.0,
            ),
            100.0,
        )

        index = (
            probability_score * 0.30
            + ev_score * 0.30
            + variation_score * 0.20
            + source_score * 0.20
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

        selected_outcome = self._safe_string(
            best_odd.get(
                "outcome",
                "",
            )
        )

        if not selected_outcome:
            return None

        # ------------------------------------------------------
        # REFERÊNCIA DO MERCADO
        # ------------------------------------------------------

        references = (
            self._calculate_market_reference(
                event
            )
        )

        selected_reference = references.get(
            selected_outcome,
            {},
        )

        fair_probability = (
            self._safe_float(
                selected_reference.get(
                    "fair_probability",
                    0,
                )
            )
        )

        reference_odd = (
            self._safe_float(
                selected_reference.get(
                    "median_odd",
                    0,
                )
            )
        )

        sources = int(
            self._safe_float(
                selected_reference.get(
                    "sources",
                    0,
                )
            )
        )

        implied_probability = (
            100.0 / odd
            if odd > 0
            else 0.0
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        expected_value = (
            self._calculate_expected_value(
                fair_probability,
                odd,
            )
        )

        # ------------------------------------------------------
        # VARIAÇÃO
        # ------------------------------------------------------

        variation = (
            self._market_variation(
                odd,
                reference_odd,
            )
        )

        # ------------------------------------------------------
        # RISCO
        # ------------------------------------------------------

        risk = self._risk_level(
            fair_probability,
            expected_value,
            variation,
            sources,
        )

        # ------------------------------------------------------
        # ÍNDICE
        # ------------------------------------------------------

        oddreal_index = (
            self._calculate_oddreal_index(
                probability=fair_probability,
                expected_value=expected_value,
                market_variation=variation,
                sources=sources,
            )
        )

        # ------------------------------------------------------
        # CONFIANÇA
        # ------------------------------------------------------

        confidence = (
            self._confidence_level(
                oddreal_index,
                sources,
            )
        )

        # ------------------------------------------------------
        # VALUE BET
        # ------------------------------------------------------

        is_value = (
            expected_value
            >= valuebet_engine.minimum_ev
        )

        # ------------------------------------------------------
        # IDENTIFICAÇÃO
        # ------------------------------------------------------

        event_id = event.get(
            "id",
            event.get(
                "event_id",
                "",
            ),
        )

        return {

            "id":
                event_id,

            "event_id":
                event_id,

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
            # PROBABILIDADES
            # --------------------------------------------------

            "probability":
                round(
                    fair_probability,
                    3,
                ),

            "fair_probability":
                round(
                    fair_probability,
                    3,
                ),

            "implied_probability":
                round(
                    implied_probability,
                    3,
                ),

            "probability_source":
                "consenso_mediano_normalizado",

            # --------------------------------------------------
            # VALOR
            # --------------------------------------------------

            "expected_value":
                round(
                    expected_value,
                    3,
                ),

            "is_value_bet":
                is_value,

            "classification":
                valuebet_engine.classify(
                    expected_value
                ),

            # --------------------------------------------------
            # MERCADO
            # --------------------------------------------------

            "average_odd":
                round(
                    reference_odd,
                    3,
                ),

            "market_reference_odd":
                round(
                    reference_odd,
                    3,
                ),

            "market_variation":
                round(
                    variation,
                    3,
                ),

            "market_sources":
                sources,

            # --------------------------------------------------
            # ÍNDICE
            # --------------------------------------------------

            "oddreal_index":
                oddreal_index,

            "confidence_level":
                confidence,

            "risk":
                risk,
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
        Identifica oportunidades com EV acima
        do limite configurado.
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
        """
        Retorna a análise com maior Índice OddReal.
        """

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
        """
        Retorna a melhor oportunidade encontrada.
        """

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
        Gera o resumo geral.
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

            "risk_distribution":
                risks,

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
    # MÉDIA DO ÍNDICE
    # ==========================================================

    @staticmethod
    def _average_index(
        analyses: List[
            Dict[str, Any]
        ],
    ) -> float:
        """
        Calcula a média do Índice OddReal.
        """

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
