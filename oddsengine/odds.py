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
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OddsEngine:
    """
    Motor quantitativo central do OddReal.

    Todas as probabilidades expostas ao restante do sistema
    são representadas em percentual (0 a 100).
    """

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

            Odd 2.00
            Probabilidade = 50%

        Retorno:
            percentual entre 0 e 100.
        """

        try:

            odd = float(odd)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if odd <= 0:

            return 0.0

        probability = (
            100.0 / odd
        )

        return round(
            min(
                probability,
                100.0,
            ),
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
        Calcula o Valor Esperado (EV) em percentual.

        probability:
            Probabilidade em percentual.

        odd:
            Odd decimal.

        Fórmula:

            EV = (p × odd) - 1

        O resultado é convertido para percentual.

        Exemplo:

            Probabilidade estimada = 60%
            Odd = 2.00

            EV = (0.60 × 2.00) - 1
               = 0.20
               = 20%
        """

        try:

            probability = float(
                probability
            )

            odd = float(
                odd
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if odd <= 0:

            return 0.0

        probability_decimal = (
            probability / 100.0
        )

        ev = (
            probability_decimal * odd
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
        Calcula o Índice OddReal.

        O índice combina:

        - probabilidade estimada;
        - valor esperado.

        O objetivo é criar uma pontuação simples
        de 0 a 100 para facilitar a leitura do usuário.

        Importante:
        o índice não representa garantia de resultado.
        """

        try:

            probability = float(
                probability
            )

            ev = float(
                ev
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0

        probability = max(
            0.0,
            min(
                probability,
                100.0,
            ),
        )

        # O EV recebe peso limitado para impedir
        # que valores extremos dominem completamente
        # o índice.

        positive_ev = max(
            0.0,
            ev,
        )

        ev_component = min(
            positive_ev * 0.75,
            25.0,
        )

        score = (
            probability * 0.75
        ) + ev_component

        return max(
            0,
            min(
                int(
                    round(score)
                ),
                100,
            ),
        )

    # ==========================================================
    # NÍVEL DE CONFIANÇA
    # ==========================================================

    def confidence_level(
        self,
        index: int,
    ) -> str:
        """
        Classifica a confiança da oportunidade.
        """

        try:

            index = int(
                index
            )

        except (
            TypeError,
            ValueError,
        ):

            index = 0

        if index >= 85:

            return "Muito Alta"

        if index >= 70:

            return "Alta"

        if index >= 55:

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
        Classifica o risco utilizando os indicadores
        disponíveis.

        É uma classificação auxiliar e não uma
        previsão de resultado.
        """

        try:

            probability = float(
                probability
            )

            ev = float(
                ev
            )

        except (
            TypeError,
            ValueError,
        ):

            return "Alto"

        if (
            probability >= 70
            and ev >= 10
        ):

            return "Baixo"

        if (
            probability >= 55
            and ev >= 5
        ):

            return "Moderado"

        return "Alto"

    # ==========================================================
    # CONSENSO DE MERCADO
    # ==========================================================

    def market_consensus(
        self,
        bookmakers: List[Dict[str, Any]],
    ) -> float:
        """
        Calcula a média das odds fornecidas.

        Espera uma lista no formato:

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

        odds: List[float] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            odd = bookmaker.get(
                "odd"
            )

            try:

                odd = float(
                    odd
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

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
        Calcula quanto a melhor odd está acima ou abaixo
        da média do mercado.

        Retorno em percentual.

        Exemplo:

            Melhor odd = 2.20
            Média = 2.00

            Variação = +10%
        """

        try:

            best_odd = float(
                best_odd
            )

            average_odd = float(
                average_odd
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if (
            best_odd <= 0
            or average_odd <= 0
        ):

            return 0.0

        variation = (
            (
                best_odd
                - average_odd
            )
            / average_odd
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
        minimum_ev: float = 5.0,
    ) -> bool:
        """
        Determina se a oportunidade ultrapassa
        o EV mínimo configurado.
        """

        try:

            ev = float(
                ev
            )

            minimum_ev = float(
                minimum_ev
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

        return ev >= minimum_ev

    # ==========================================================
    # ANÁLISE COMPLETA DO EVENTO
    # ==========================================================

    def analyze_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa a análise completa de um evento.

        O evento precisa conter:

            best_odd = {
                "odd": 2.10,
                ...
            }

        Caso o evento já possua uma probabilidade calculada
        pelo sistema, ela será utilizada.

        Caso contrário, a probabilidade implícita da odd
        será utilizada como referência.
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
                "probability": 0.0,
                "expected_value": 0.0,
                "oddreal_index": 0,
                "confidence_level": "Baixa",
                "average_odd": 0.0,
                "market_variation": 0.0,
                "risk": "Alto",
                "is_value_bet": False,
            }

        odd = best.get(
            "odd"
        )

        try:

            odd = float(
                odd
            )

        except (
            TypeError,
            ValueError,
        ):

            odd = 0.0

        if odd <= 0:

            return {
                **event,
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
        # Probabilidade
        # ------------------------------------------------------

        supplied_probability = event.get(
            "confidence"
        )

        if supplied_probability is None:

            probability = (
                self.implied_probability(
                    odd
                )
            )

        else:

            try:

                probability = float(
                    supplied_probability
                )

            except (
                TypeError,
                ValueError,
            ):

                probability = (
                    self.implied_probability(
                        odd
                    )
                )

        probability = max(
            0.0,
            min(
                probability,
                100.0,
            ),
        )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        ev = self.expected_value(
            probability,
            odd,
        )

        # ------------------------------------------------------
        # Índice
        # ------------------------------------------------------

        index = self.oddreal_index(
            probability,
            ev,
        )

        # ------------------------------------------------------
        # Confiança
        # ------------------------------------------------------

        confidence_level = (
            self.confidence_level(
                index
            )
        )

        # ------------------------------------------------------
        # Mercado
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

        variation = (
            self.market_variation(
                odd,
                average_odd,
            )
        )

        # ------------------------------------------------------
        # Risco
        # ------------------------------------------------------

        risk = self.risk_level(
            probability,
            ev,
        )

        # ------------------------------------------------------
        # Value Bet
        # ------------------------------------------------------

        value_bet = self.is_value_bet(
            ev
        )

        # ------------------------------------------------------
        # Resultado
        # ------------------------------------------------------

        return {

            **event,

            "best_odd": best,

            "selected_outcome": best.get(
                "outcome"
            ),

            "selected_bookmaker": best.get(
                "bookmaker"
            ),

            "selected_market": best.get(
                "market"
            ),

            "odd": odd,

            "probability": round(
                probability,
                2,
            ),

            "expected_value": ev,

            "oddreal_index": index,

            "confidence_level": (
                confidence_level
            ),

            "average_odd": average_odd,

            "market_variation": variation,

            "risk": risk,

            "is_value_bet": value_bet,

        }


odds_engine = OddsEngine()
