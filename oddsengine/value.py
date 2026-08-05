"""
OddReal 2.0
Motor de Value Bets

Arquivo:
oddsengine/value.py

Responsável por:
- Probabilidade implícita;
- Valor esperado (EV);
- Identificação de Value Bets;
- Classificação das oportunidades;
- Seleção da melhor Value Bet;
- Compatibilidade com versões anteriores do OddsEngine.

Não consulta API.
Não utiliza IA.
Não altera bookmakers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error


class ValueBetEngine:
    """
    Motor responsável exclusivamente pela análise
    matemática de Value Bets.

    IMPORTANTE:

    A probabilidade utilizada para calcular EV deve
    representar a probabilidade estimada pelo OddReal.

    A odd NÃO deve ser utilizada para criar a
    própria probabilidade estimada, pois isso
    produziria um cálculo circular.

    probability:
        Probabilidade estimada em escala 0-100.

    odd:
        Odd decimal oferecida pela casa.
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
    ) -> None:

        self.minimum_ev = float(
            minimum_ev
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
        Converte um valor para float com segurança.

        Evita que valores inválidos interrompam
        o processamento do pipeline.
        """

        try:

            if value is None:
                return default

            result = float(value)

            # NaN
            if result != result:
                return default

            # infinito
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
        Calcula a probabilidade implícita da odd.

        Fórmula:

            P = 1 / odd

        Retorno em escala 0-100.

        Exemplos:

            Odd 2.00 -> 50.00%
            Odd 1.50 -> 66.67%
            Odd 4.00 -> 25.00%
            Odd 8.00 -> 12.50%
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 0:

            return 0.0

        return round(
            (1.0 / odd) * 100.0,
            4,
        )

    # ==========================================================
    # EXPECTED VALUE
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o Valor Esperado (EV) percentual.

        probability:
            Probabilidade estimada pelo OddReal,
            em escala 0-100.

        odd:
            Odd decimal.

        Fórmula:

            EV =
            ((probabilidade / 100) × odd - 1) × 100

        Exemplo:

            probability = 15%
            odd = 8.00

            0.15 × 8 = 1.20

            1.20 - 1 = 0.20

            EV = 20%

        IMPORTANTE:

        A probabilidade deve ser independente da
        odd analisada.

        Não devemos fazer:

            probability = 100 / odd

        para depois calcular EV.

        Isso faria o EV ser sempre aproximadamente
        zero e destruiria a identificação de valor.
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if (
            probability <= 0
            or odd <= 0
        ):

            return 0.0

        # Proteção contra probabilidades impossíveis.
        if probability > 100:

            probability = 100.0

        probability_decimal = (
            probability / 100.0
        )

        ev = (
            probability_decimal * odd
            - 1.0
        ) * 100.0

        return round(
            ev,
            4,
        )

    # ==========================================================
    # VALUE BET
    # ==========================================================

    def is_value_bet(
        self,
        probability: float,
        odd: float,
    ) -> bool:
        """
        Determina se uma oportunidade é Value Bet.

        Regra:

            EV >= minimum_ev

        Com minimum_ev padrão de 5%:

            EV < 5%  -> não é Value Bet
            EV >= 5% -> é Value Bet
        """

        ev = self.expected_value(
            probability,
            odd,
        )

        return (
            ev >= self.minimum_ev
        )

    # ==========================================================
    # CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def classify(
        expected_value: float,
    ) -> str:
        """
        Classifica a força matemática da oportunidade.
        """

        ev = ValueBetEngine._safe_float(
            expected_value
        )

        if ev >= 20:

            return "Excelente"

        if ev >= 15:

            return "Muito Forte"

        if ev >= 10:

            return "Forte"

        if ev >= 5:

            return "Value Bet"

        if ev > 0:

            return "Positivo"

        return "Sem Valor"

    # ==========================================================
    # ANALISAR
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
        Analisa as oportunidades recebidas
        pelo Analyzer.

        A função:

        1. identifica a odd;
        2. obtém a probabilidade estimada;
        3. calcula o EV;
        4. verifica se é Value Bet;
        5. cria uma estrutura padronizada.

        A probabilidade principal é:

            probability

        Fallback de compatibilidade:

            confidence

        IMPORTANTE:

        Não utilizamos a probabilidade implícita da
        própria odd como probabilidade estimada.
        """

        if not isinstance(
            analyses,
            list,
        ):

            return []

        opportunities: List[
            Dict[str, Any]
        ] = []

        for event in analyses:

            if not isinstance(
                event,
                dict,
            ):

                continue

            # ==================================================
            # ODD
            # ==================================================

            best_odd = event.get(
                "best_odd",
                {},
            )

            if not isinstance(
                best_odd,
                dict,
            ):

                best_odd = {}

            odd = self._safe_float(
                event.get(
                    "odd",
                    best_odd.get(
                        "odd",
                        0,
                    ),
                )
            )

            if odd <= 0:

                continue

            # ==================================================
            # PROBABILIDADE ESTIMADA
            # ==================================================

            probability_value = event.get(
                "probability",
                None,
            )

            # Compatibilidade com versões anteriores
            if probability_value is None:

                probability_value = event.get(
                    "confidence",
                    0,
                )

            probability = self._safe_float(
                probability_value
            )

            if probability <= 0:

                continue

            # Proteção contra valores impossíveis.

            if probability > 100:

                probability = 100.0

            # ==================================================
            # PROBABILIDADE IMPLÍCITA
            # ==================================================

            implied_probability = (
                self.implied_probability(
                    odd
                )
            )

            # ==================================================
            # EV
            # ==================================================

            ev = self.expected_value(
                probability,
                odd,
            )

            # ==================================================
            # VALUE BET
            # ==================================================

            is_value = (
                ev >= self.minimum_ev
            )

            # ==================================================
            # CLASSIFICAÇÃO
            # ==================================================

            classification = (
                self.classify(
                    ev
                )
            )

            # ==================================================
            # ESTRUTURA DA OPORTUNIDADE
            # ==================================================

            opportunity = {

                "event_id":
                    event.get(
                        "event_id",
                        event.get(
                            "id",
                            "",
                        ),
                    ),

                "sport":
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

                "market":
                    event.get(
                        "selected_market",
                        best_odd.get(
                            "market",
                            "",
                        ),
                    ),

                "selection":
                    event.get(
                        "selected_outcome",
                        best_odd.get(
                            "outcome",
                            "",
                        ),
                    ),

                "bookmaker":
                    event.get(
                        "selected_bookmaker",
                        best_odd.get(
                            "bookmaker",
                            "",
                        ),
                    ),

                # ------------------------------------------
                # ODDS
                # ------------------------------------------

                "odd":
                    round(
                        odd,
                        3,
                    ),

                # ------------------------------------------
                # PROBABILIDADES
                # ------------------------------------------

                "probability":
                    round(
                        probability,
                        3,
                    ),

                "implied_probability":
                    round(
                        implied_probability,
                        3,
                    ),

                # ------------------------------------------
                # EV
                # ------------------------------------------

                "expected_value":
                    round(
                        ev,
                        3,
                    ),

                # ------------------------------------------
                # ODDREAL
                # ------------------------------------------

                "oddreal_index":
                    self._safe_float(
                        event.get(
                            "oddreal_index",
                            0,
                        )
                    ),

                "confidence_level":
                    event.get(
                        "confidence_level",
                        "",
                    ),

                # ------------------------------------------
                # MERCADO
                # ------------------------------------------

                "average_odd":
                    self._safe_float(
                        event.get(
                            "average_odd",
                            0,
                        )
                    ),

                "market_variation":
                    self._safe_float(
                        event.get(
                            "market_variation",
                            0,
                        )
                    ),

                # ------------------------------------------
                # RISCO
                # ------------------------------------------

                "risk":
                    event.get(
                        "risk",
                        "Alto",
                    ),

                # ------------------------------------------
                # CLASSIFICAÇÃO
                # ------------------------------------------

                "classification":
                    classification,

                # ------------------------------------------
                # FLAG DEFINITIVA
                # ------------------------------------------

                "is_value_bet":
                    is_value,

            }

            # ==================================================
            # APENAS VALUE BETS
            # ==================================================

            if not is_value:

                continue

            opportunities.append(
                opportunity
            )

        info(
            f"{len(opportunities)} "
            "Value Bets encontradas."
        )

        return opportunities

    # ==========================================================
    # MELHOR VALUE BET
    # ==========================================================

    def best_value_bet(
        self,
        opportunities: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Retorna a melhor Value Bet.

        Critério principal:
            maior EV.

        Critério de desempate:
            maior Índice OddReal.
        """

        if not isinstance(
            opportunities,
            list,
        ):

            return None

        valid = [

            item

            for item in opportunities

            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "is_value_bet",
                    False,
                )
            )
        ]

        if not valid:

            return None

        return max(
            valid,
            key=lambda item: (
                self._safe_float(
                    item.get(
                        "expected_value",
                        0,
                    )
                ),

                self._safe_float(
                    item.get(
                        "oddreal_index",
                        0,
                    )
                ),
            ),
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna o estado atual do motor.
        """

        return {

            "service":
                "ValueBetEngine",

            "minimum_ev":
                self.minimum_ev,

            "configured":
                True,

        }


# ==========================================================
# COMPATIBILIDADE COM VERSÕES ANTERIORES
# ==========================================================

# Alguns módulos antigos do OddReal podem importar
# ValueEngine em vez de ValueBetEngine.

ValueEngine = ValueBetEngine


# ==========================================================
# INSTÂNCIAS GLOBAIS
# ==========================================================

valuebet_engine = ValueBetEngine()

# Compatibilidade com módulos que ainda utilizam
# o nome antigo "value_engine".

value_engine = valuebet_engine
