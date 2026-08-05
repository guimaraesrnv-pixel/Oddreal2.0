"""
OddReal 2.0
Motor de análise probabilística de mercado.

Arquivo:
    oddsengine/value.py

Responsável por:
    - conversão segura de valores;
    - probabilidade implícita;
    - normalização de probabilidades;
    - cálculo de overround/margem;
    - análise estatística das odds;
    - classificação de consistência do mercado;
    - compatibilidade com versões anteriores.

Este módulo NÃO:
    - consulta API;
    - coleta dados;
    - utiliza IA;
    - altera bookmakers;
    - depende do Streamlit.
"""

from __future__ import annotations

from statistics import median
from typing import Any, Dict, List, Optional

from modules.logger import info


class ValueBetEngine:
    """
    Motor matemático de análise de mercado.

    A responsabilidade deste módulo é transformar odds
    observadas em indicadores estatísticos.

    IMPORTANTE:

    A probabilidade implícita de uma odd é uma medida
    derivada da própria odd.

    Portanto, ela NÃO deve ser tratada como uma
    probabilidade independente de previsão.
    """

    def __init__(
        self,
        minimum_sources: int = 2,
    ) -> None:

        self.minimum_sources = max(
            1,
            int(minimum_sources),
        )

        info(
            "ValueBetEngine OddReal 2.0 iniciado."
        )

    # ==========================================================
    # CONVERSÃO SEGURA
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Converte qualquer valor numérico para float.

        Protege contra:
            - None;
            - strings inválidas;
            - NaN;
            - infinito.
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
    # ODD VÁLIDA
    # ==========================================================

    @classmethod
    def valid_odd(
        cls,
        odd: Any,
    ) -> float:
        """
        Retorna uma odd válida.

        Odds decimais precisam ser maiores que 1.
        """

        value = cls._safe_float(
            odd
        )

        if value <= 1.0:
            return 0.0

        return value

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    @classmethod
    def implied_probability(
        cls,
        odd: float,
    ) -> float:
        """
        Calcula a probabilidade implícita.

        Fórmula:

            P = 1 / odd

        Retorno:
            percentual entre 0 e 100.
        """

        odd = cls.valid_odd(
            odd
        )

        if odd <= 1.0:
            return 0.0

        probability = (
            1.0 / odd
        ) * 100.0

        return round(
            probability,
            4,
        )

    # ==========================================================
    # PROBABILIDADES DO MERCADO
    # ==========================================================

    @classmethod
    def market_probabilities(
        cls,
        outcomes: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, float]:
        """
        Calcula probabilidades implícitas de um mercado.

        Exemplo:

            Casa:
                2.00
                3.00
                4.00

        Probabilidades:

            50.00
            33.33
            25.00

        A soma será superior a 100% quando houver
        margem da casa.

        Esta função NÃO remove a margem.

        Para isso utilize:

            normalized_probabilities()
        """

        probabilities: Dict[
            str,
            float,
        ] = {}

        if not isinstance(
            outcomes,
            list,
        ):
            return probabilities

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

            odd = cls.valid_odd(
                outcome.get(
                    "odd"
                )
            )

            if not name:
                continue

            if odd <= 1.0:
                continue

            probability = (
                cls.implied_probability(
                    odd
                )
            )

            if probability <= 0:
                continue

            probabilities[name] = (
                probabilities.get(
                    name,
                    0.0,
                )
                + probability
            )

        return {
            key: round(
                value,
                4,
            )
            for key, value in probabilities.items()
        }

    # ==========================================================
    # OVERROUND
    # ==========================================================

    @classmethod
    def overround(
        cls,
        probabilities: Dict[
            str,
            float,
        ],
    ) -> float:
        """
        Calcula a margem matemática implícita.

        Fórmula:

            Overround = soma das probabilidades - 100

        Exemplo:

            108.33 - 100 = 8.33%

        Quanto maior o valor, maior a margem
        implícita daquele conjunto de odds.
        """

        if not isinstance(
            probabilities,
            dict,
        ):
            return 0.0

        total = sum(
            cls._safe_float(
                value
            )
            for value in probabilities.values()
        )

        if total <= 0:
            return 0.0

        return round(
            total - 100.0,
            4,
        )

    # ==========================================================
    # PROBABILIDADES NORMALIZADAS
    # ==========================================================

    @classmethod
    def normalized_probabilities(
        cls,
        probabilities: Dict[
            str,
            float,
        ],
    ) -> Dict[str, float]:
        """
        Remove matematicamente o overround por normalização.

        Exemplo:

            A = 50
            B = 33.33
            C = 25

            total = 108.33

        Então:

            A = 50 / 108.33 × 100
            B = 33.33 / 108.33 × 100
            C = 25 / 108.33 × 100

        O resultado soma aproximadamente 100%.
        """

        if not isinstance(
            probabilities,
            dict,
        ):
            return {}

        valid = {
            name: cls._safe_float(
                probability
            )
            for name, probability
            in probabilities.items()
            if cls._safe_float(
                probability
            ) > 0
        }

        total = sum(
            valid.values()
        )

        if total <= 0:
            return {}

        normalized = {}

        for name, probability in valid.items():

            normalized[name] = round(
                (
                    probability
                    / total
                )
                * 100.0,
                4,
            )

        return normalized

    # ==========================================================
    # ANÁLISE COMPLETA DO MERCADO
    # ==========================================================

    @classmethod
    def analyze_market(
        cls,
        outcomes: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Analisa matematicamente um mercado.

        Retorna:

            - probabilidades implícitas;
            - overround;
            - probabilidades normalizadas;
            - quantidade de resultados;
            - status de consistência.

        Não produz recomendação de aposta.
        """

        probabilities = (
            cls.market_probabilities(
                outcomes
            )
        )

        overround_value = (
            cls.overround(
                probabilities
            )
        )

        normalized = (
            cls.normalized_probabilities(
                probabilities
            )
        )

        return {
            "implied_probabilities":
                probabilities,

            "normalized_probabilities":
                normalized,

            "overround":
                overround_value,

            "outcome_count":
                len(
                    normalized
                ),

            "valid":
                bool(
                    normalized
                ),
        }

    # ==========================================================
    # ESTATÍSTICAS DAS ODDS
    # ==========================================================

    @classmethod
    def odds_statistics(
        cls,
        odds: List[Any],
    ) -> Dict[str, float]:
        """
        Calcula estatísticas básicas de um conjunto
        de odds provenientes de diferentes casas.
        """

        valid = []

        for odd in odds:

            value = cls.valid_odd(
                odd
            )

            if value > 1.0:
                valid.append(
                    value
                )

        if not valid:

            return {
                "count": 0,
                "minimum": 0.0,
                "maximum": 0.0,
                "average": 0.0,
                "median": 0.0,
                "variation_percent": 0.0,
            }

        minimum = min(
            valid
        )

        maximum = max(
            valid
        )

        average = (
            sum(valid)
            / len(valid)
        )

        middle = median(
            valid
        )

        variation = 0.0

        if minimum > 0:

            variation = (
                (
                    maximum
                    - minimum
                )
                / minimum
            ) * 100.0

        return {
            "count":
                len(valid),

            "minimum":
                round(
                    minimum,
                    4,
                ),

            "maximum":
                round(
                    maximum,
                    4,
                ),

            "average":
                round(
                    average,
                    4,
                ),

            "median":
                round(
                    middle,
                    4,
                ),

            "variation_percent":
                round(
                    variation,
                    4,
                ),
        }

    # ==========================================================
    # CONSISTÊNCIA DO MERCADO
    # ==========================================================

    @classmethod
    def market_consistency(
        cls,
        odds: List[Any],
    ) -> str:
        """
        Classifica a consistência estatística das odds.

        Não significa:
            "boa aposta".

        Significa apenas que as casas apresentam
        cotações relativamente próximas ou distantes.
        """

        statistics = (
            cls.odds_statistics(
                odds
            )
        )

        count = statistics[
            "count"
        ]

        variation = statistics[
            "variation_percent"
        ]

        if count < cls.minimum_sources:
            return "Insuficiente"

        if variation <= 5.0:
            return "Alta"

        if variation <= 12.0:
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # SCORE DE CONSISTÊNCIA
    # ==========================================================

    @classmethod
    def consistency_score(
        cls,
        odds: List[Any],
    ) -> float:
        """
        Produz um índice estatístico de consistência.

        100:
            mercado extremamente uniforme.

        0:
            mercado muito disperso.

        Este índice NÃO representa probabilidade de vitória
        e NÃO representa retorno esperado.
        """

        statistics = (
            cls.odds_statistics(
                odds
            )
        )

        count = statistics[
            "count"
        ]

        variation = statistics[
            "variation_percent"
        ]

        if count == 0:
            return 0.0

        # Quanto menor a variação,
        # maior a consistência.
        score = max(
            0.0,
            100.0 - (
                variation * 4.0
            ),
        )

        # Poucas fontes reduzem a confiança estatística.
        if count == 1:
            score *= 0.50

        elif count == 2:
            score *= 0.75

        elif count == 3:
            score *= 0.90

        return round(
            min(
                100.0,
                score,
            ),
            2,
        )

    # ==========================================================
    # ANALISAR SELEÇÕES
    # ==========================================================

    def analyze(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Compatibilidade com o fluxo anterior do OddReal.

        Recebe análises já produzidas pelo Analyzer e
        acrescenta indicadores matemáticos de mercado.

        Não cria Value Bets.
        """

        if not isinstance(
            analyses,
            list,
        ):
            return []

        results = []

        for item in analyses:

            if not isinstance(
                item,
                dict,
            ):
                continue

            result = dict(
                item
            )

            odd = self.valid_odd(
                result.get(
                    "odd"
                )
            )

            if odd <= 1.0:
                continue

            result[
                "implied_probability"
            ] = round(
                self.implied_probability(
                    odd
                ),
                3,
            )

            result[
                "market_consistency"
            ] = result.get(
                "market_consistency",
                "Insuficiente",
            )

            result[
                "consistency_score"
            ] = self._safe_float(
                result.get(
                    "consistency_score",
                    0,
                )
            )

            results.append(
                result
            )

        info(
            f"{len(results)} análises "
            "probabilísticas processadas."
        )

        return results

    # ==========================================================
    # COMPATIBILIDADE
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Mantido apenas para compatibilidade estrutural.

        NÃO deve ser usado pela nova interface como
        recomendação de aposta.

        Calcula matematicamente:

            (P × odd - 1) × 100
        """

        probability = self._safe_float(
            probability
        )

        odd = self.valid_odd(
            odd
        )

        if (
            probability <= 0
            or odd <= 1.0
        ):
            return 0.0

        probability = min(
            100.0,
            probability,
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
            4,
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna o estado do motor.
        """

        return {
            "service":
                "ValueBetEngine",

            "minimum_sources":
                self.minimum_sources,

            "configured":
                True,
        }


# ==============================================================
# COMPATIBILIDADE COM VERSÕES ANTIGAS
# ==============================================================

ValueEngine = ValueBetEngine


# ==============================================================
# INSTÂNCIAS GLOBAIS
# ==============================================================

valuebet_engine = ValueBetEngine()

value_engine = valuebet_engine
