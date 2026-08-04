"""
OddReal 2.0
Motor de Cálculo de Odds

Responsável por:

- Probabilidade implícita
- Valor esperado (EV)
- Índice OddReal
- Nível de confiança
- Nível de risco
- Consenso de mercado
- Variação da odd
- Classificação de Value Bet

Todas as probabilidades são trabalhadas em percentual:
0 a 100.

Todas as odds são trabalhadas no formato decimal.
"""

from __future__ import annotations

from typing import Any, Dict, List


class OddsEngine:
    """
    Motor quantitativo central do OddReal 2.0.

    Este módulo é responsável exclusivamente pelos
    cálculos matemáticos utilizados pelo sistema.

    Não realiza:
    - chamadas de API;
    - acesso ao banco de dados;
    - geração de textos por IA;
    - interface gráfica;
    - coleta de eventos.
    """

    def __init__(
        self,
        minimum_ev: float = 5.0,
    ) -> None:

        self.minimum_ev = float(
            minimum_ev
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

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """
        Mantém um valor dentro de um intervalo.
        """

        return max(
            minimum,
            min(
                value,
                maximum,
            ),
        )

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    def implied_probability(
        self,
        odd: float,
    ) -> float:
        """
        Calcula a probabilidade implícita de uma odd decimal.

        Exemplo:

            Odd = 2.00
            Probabilidade = 50%
        """

        odd_value = self._safe_float(
            odd
        )

        if odd_value <= 0:

            return 0.0

        probability = (
            100.0 / odd_value
        )

        probability = self._clamp(
            probability,
            0.0,
            100.0,
        )

        return round(
            probability,
            2,
        )

    # ==========================================================
    # VALOR ESPERADO
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o Valor Esperado em percentual.

        probability:
            Probabilidade estimada em percentual.

        odd:
            Odd decimal.

        Fórmula:

            EV = ((probabilidade / 100) × odd - 1) × 100
        """

        probability_value = (
            self._safe_float(
                probability
            )
        )

        odd_value = self._safe_float(
            odd
        )

        if odd_value <= 0:

            return 0.0

        probability_value = self._clamp(
            probability_value,
            0.0,
            100.0,
        )

        probability_decimal = (
            probability_value / 100.0
        )

        ev = (
            probability_decimal
            * odd_value
        ) - 1.0

        return round(
            ev * 100.0,
            2,
        )

    # ==========================================================
    # ÍNDICE ODDREAL
    # ==========================================================

    def oddreal_index(
        self,
        probability: float,
        ev: float,
    ) -> int:
        """
        Calcula o Índice OddReal de 0 a 100.

        O índice combina:

        - probabilidade estimada;
        - EV positivo.

        O EV possui contribuição limitada para evitar
        que valores extremos dominem a pontuação.
        """

        probability_value = (
            self._safe_float(
                probability
            )
        )

        ev_value = self._safe_float(
            ev
        )

        probability_value = self._clamp(
            probability_value,
            0.0,
            100.0,
        )

        positive_ev = max(
            0.0,
            ev_value,
        )

        ev_component = min(
            positive_ev * 0.75,
            25.0,
        )

        score = (
            probability_value * 0.75
        ) + ev_component

        return int(
            self._clamp(
                round(score),
                0,
                100,
            )
        )

    # ==========================================================
    # NÍVEL DE CONFIANÇA
    # ==========================================================

    def confidence_level(
        self,
        index: int,
    ) -> str:
        """
        Classifica o Índice OddReal.
        """

        index_value = int(
            self._safe_float(
                index
            )
        )

        if index_value >= 85:

            return "Muito Alta"

        if index_value >= 70:

            return "Alta"

        if index_value >= 55:

            return "Média"

        return "Baixa"

    # ==========================================================
    # NÍVEL DE RISCO
    # ==========================================================

    def risk_level(
        self,
        probability: float,
        ev: float,
    ) -> str:
        """
        Classificação auxiliar de risco.

        Não representa garantia de resultado.
        """

        probability_value = (
            self._safe_float(
                probability
            )
        )

        ev_value = self._safe_float(
            ev
        )

        if (
            probability_value >= 70
            and ev_value >= 10
        ):

            return "Baixo"

        if (
            probability_value >= 55
            and ev_value >= 5
        ):

            return "Moderado"

        return "Alto"

    # ==========================================================
    # CONSENSO DE MERCADO
    # ==========================================================

    def market_consensus(
        self,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> float:
        """
        Calcula a média das odds disponíveis.

        Formato esperado:

            [
                {"odd": 2.10},
                {"odd": 2.15},
                {"odd": 2.05}
            ]
        """

        if not isinstance(
            bookmakers,
            list,
        ):

            return 0.0

        odds: List[
            float
        ] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            odd = self._safe_float(
                bookmaker.get(
                    "odd"
                )
            )

            if odd > 0:

                odds.append(
                    odd
                )

        if not odds:

            return 0.0

        return round(
            sum(odds)
            / len(odds),
            2,
        )

    # ==========================================================
    # VARIAÇÃO DE MERCADO
    # ==========================================================

    def market_variation(
        self,
        best_odd: float,
        average_odd: float,
    ) -> float:
        """
        Calcula a diferença percentual entre a melhor odd
        e a média do mercado.

        Exemplo:

            Melhor odd = 2.20
            Média = 2.00

            Resultado = +10%
        """

        best_value = self._safe_float(
            best_odd
        )

        average_value = self._safe_float(
            average_odd
        )

        if (
            best_value <= 0
            or average_value <= 0
        ):

            return 0.0

        variation = (
            (
                best_value
                - average_value
            )
            / average_value
        ) * 100.0

        return round(
            variation,
            2,
        )

    # ==========================================================
    # VALUE BET
    # ==========================================================

    def is_value_bet(
        self,
        ev: float,
        minimum_ev: float | None = None,
    ) -> bool:
        """
        Determina se o EV ultrapassa o limite configurado.
        """

        ev_value = self._safe_float(
            ev
        )

        threshold = (
            self.minimum_ev
            if minimum_ev is None
            else self._safe_float(
                minimum_ev,
                self.minimum_ev,
            )
        )

        return (
            ev_value >= threshold
        )

    # ==========================================================
    # EXTRAÇÃO DA PROBABILIDADE
    # ==========================================================

    def _get_probability(
        self,
        event: Dict[str, Any],
        odd: float,
    ) -> float:
        """
        Obtém a probabilidade estimada do evento.

        Ordem de prioridade:

        1. probability
        2. estimated_probability
        3. confidence

        Se nenhuma estiver disponível,
        utiliza a probabilidade implícita da odd.

        Isso mantém compatibilidade com módulos anteriores
        sem deixar 'confidence' substituir silenciosamente
        a probabilidade principal quando ela existir.
        """

        probability_keys = (
            "probability",
            "estimated_probability",
            "confidence",
        )

        for key in probability_keys:

            value = event.get(
                key
            )

            if value is None:

                continue

            try:

                probability = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if probability > 0:

                return round(
                    self._clamp(
                        probability,
                        0.0,
                        100.0,
                    ),
                    2,
                )

        return self.implied_probability(
            odd
        )

    # ==========================================================
    # ANÁLISE COMPLETA DO EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa todos os cálculos quantitativos de um evento.

        O evento deve conter:

            {
                "best_odd": {
                    "odd": 2.10,
                    "bookmaker": "...",
                    "market": "...",
                    "outcome": "..."
                }
            }

        A probabilidade já calculada por outra camada,
        quando existente, é preservada.

        Caso não exista, utiliza-se a probabilidade implícita.
        """

        if not isinstance(
            event,
            dict,
        ):

            return {}

        best = event.get(
            "best_odd"
        )

        if not isinstance(
            best,
            dict,
        ):

            return {
                **event,
                "odd": 0.0,
                "probability": 0.0,
                "expected_value": 0.0,
                "oddreal_index": 0,
                "confidence_level": "Baixa",
                "average_odd": 0.0,
                "market_variation": 0.0,
                "risk": "Alto",
                "is_value_bet": False,
            }

        odd = self._safe_float(
            best.get(
                "odd"
            )
        )

        if odd <= 0:

            return {
                **event,
                "odd": 0.0,
                "probability": 0.0,
                "expected_value": 0.0,
                "oddreal_index": 0,
                "confidence_level": "Baixa",
                "average_odd": 0.0,
                "market_variation": 0.0,
                "risk": "Alto",
                "is_value_bet": False,
            }

        # ------------------------------------------------------
        # PROBABILIDADE
        # ------------------------------------------------------

        probability = (
            self._get_probability(
                event,
                odd,
            )
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        ev = self.expected_value(
            probability,
            odd,
        )

        # ------------------------------------------------------
        # ÍNDICE
        # ------------------------------------------------------

        index = self.oddreal_index(
            probability,
            ev,
        )

        # ------------------------------------------------------
        # CONFIANÇA
        # ------------------------------------------------------

        confidence_level = (
            self.confidence_level(
                index
            )
        )

        # ------------------------------------------------------
        # ODDS DO MERCADO
        # ------------------------------------------------------

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            bookmakers = []

        average_odd = (
            self.market_consensus(
                bookmakers
            )
        )

        # ------------------------------------------------------
        # VARIAÇÃO
        # ------------------------------------------------------

        variation = (
            self.market_variation(
                odd,
                average_odd,
            )
        )

        # ------------------------------------------------------
        # RISCO
        # ------------------------------------------------------

        risk = self.risk_level(
            probability,
            ev,
        )

        # ------------------------------------------------------
        # VALUE BET
        # ------------------------------------------------------

        value_bet = (
            self.is_value_bet(
                ev
            )
        )

        # ------------------------------------------------------
        # RESULTADO
        # ------------------------------------------------------

        return {

            **event,

            "best_odd": best,

            "selected_outcome": (
                best.get(
                    "outcome"
                )
            ),

            "selected_bookmaker": (
                best.get(
                    "bookmaker"
                )
            ),

            "selected_market": (
                best.get(
                    "market"
                )
            ),

            "odd": round(
                odd,
                3,
            ),

            "probability": round(
                probability,
                2,
            ),

            "expected_value": round(
                ev,
                2,
            ),

            "oddreal_index": index,

            "confidence_level": (
                confidence_level
            ),

            "average_odd": round(
                average_odd,
                2,
            ),

            "market_variation": round(
                variation,
                2,
            ),

            "risk": risk,

            "is_value_bet": (
                value_bet
            ),

        }

    # ==========================================================
    # ANÁLISE EM LOTE
    # ==========================================================

    def analyze_many(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Analisa vários eventos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        results: List[
            Dict[str, Any]
        ] = []

        for event in events:

            try:

                result = (
                    self.analyze_event(
                        event
                    )
                )

                if result:

                    results.append(
                        result
                    )

            except Exception:

                continue

        return results


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

odds_engine = OddsEngine()
