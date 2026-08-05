"""
OddReal 2.0
Motor de Cálculo de Odds

Responsável por:

- Probabilidade implícita;
- Probabilidade estimada pelo OddReal;
- Valor esperado (EV);
- Índice OddReal;
- Nível de confiança;
- Nível de risco;
- Consenso de mercado;
- Variação da odd;
- Classificação de Value Bet.

IMPORTANTE:

A probabilidade implícita da odd NÃO é considerada uma
probabilidade estimada pelo OddReal.

Exemplo:

Odd = 2.00
Probabilidade implícita = 50%

Isso NÃO significa que o OddReal estima 50%.

Para calcular EV de forma real, o sistema precisa de uma
probabilidade independente fornecida pelo Analyzer,
modelo estatístico ou outra camada quantitativa.

Quando essa probabilidade independente não existir,
o EV será considerado 0 e a oportunidade NÃO será
classificada como Value Bet.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OddsEngine:
    """
    Motor quantitativo central do OddReal.

    Todas as probabilidades expostas ao restante do sistema
    são representadas em percentual, entre 0 e 100.
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

            Odd = 2.00
            Probabilidade implícita = 50%

        Esta probabilidade representa o preço do mercado.

        Ela NÃO representa uma previsão independente do OddReal.
        """

        try:
            odd = float(odd)
        except (TypeError, ValueError):
            return 0.0

        if odd <= 0:
            return 0.0

        probability = 100.0 / odd

        return round(
            max(
                0.0,
                min(
                    probability,
                    100.0,
                ),
            ),
            2,
        )

    # ==========================================================
    # NORMALIZAÇÃO DE PROBABILIDADE
    # ==========================================================

    @staticmethod
    def normalize_probability(
        probability: Any,
    ) -> Optional[float]:
        """
        Normaliza uma probabilidade para percentual.

        Aceita:

            60
            60.0
            0.60

        Valores entre 0 e 1 são interpretados como
        probabilidade decimal.

        Valores acima de 1 são interpretados como percentual.

        Retorna None quando não existe uma probabilidade válida.
        """

        if probability is None:
            return None

        try:
            value = float(probability)
        except (TypeError, ValueError):
            return None

        if value < 0:
            return None

        # Probabilidade decimal.
        if 0.0 <= value <= 1.0:
            value *= 100.0

        value = max(
            0.0,
            min(
                value,
                100.0,
            ),
        )

        return round(
            value,
            2,
        )

    # ==========================================================
    # PROBABILIDADE ESTIMADA
    # ==========================================================

    def get_estimated_probability(
        self,
        event: Dict[str, Any],
    ) -> Optional[float]:
        """
        Procura uma probabilidade independente calculada
        pelo OddReal.

        A prioridade é:

        1. estimated_probability
        2. model_probability
        3. fair_probability
        4. probability
        5. probability_estimate
        6. win_probability

        IMPORTANTE:

        "confidence" NÃO é utilizada como probabilidade.

        Confiança e probabilidade são indicadores diferentes.
        """

        if not isinstance(event, dict):
            return None

        probability_keys = (
            "estimated_probability",
            "model_probability",
            "fair_probability",
            "probability",
            "probability_estimate",
            "win_probability",
        )

        for key in probability_keys:

            if key not in event:
                continue

            probability = self.normalize_probability(
                event.get(key)
            )

            if probability is not None:
                return probability

        return None

    # ==========================================================
    # VALOR ESPERADO
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o Valor Esperado (EV).

        probability:
            Probabilidade estimada em percentual.

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

        normalized_probability = (
            self.normalize_probability(
                probability
            )
        )

        if normalized_probability is None:
            return 0.0

        try:
            odd = float(odd)
        except (TypeError, ValueError):
            return 0.0

        if odd <= 0:
            return 0.0

        probability_decimal = (
            normalized_probability / 100.0
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

        O resultado varia entre 0 e 100.

        IMPORTANTE:

        O índice somente deve ser interpretado como indicador
        quantitativo quando existir uma probabilidade estimada
        independente do preço da odd.
        """

        normalized_probability = (
            self.normalize_probability(
                probability
            )
        )

        try:
            ev = float(ev)
        except (TypeError, ValueError):
            ev = 0.0

        if normalized_probability is None:
            return 0

        normalized_probability = max(
            0.0,
            min(
                normalized_probability,
                100.0,
            ),
        )

        positive_ev = max(
            0.0,
            ev,
        )

        # Limita a contribuição do EV.
        ev_component = min(
            positive_ev * 0.75,
            25.0,
        )

        score = (
            normalized_probability * 0.75
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
        Classifica a força quantitativa da oportunidade.
        """

        try:
            index = int(index)
        except (TypeError, ValueError):
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
        quantitativos disponíveis.

        Esta classificação não representa garantia
        de resultado.
        """

        normalized_probability = (
            self.normalize_probability(
                probability
            )
        )

        try:
            ev = float(ev)
        except (TypeError, ValueError):
            return "Alto"

        if normalized_probability is None:
            return "Alto"

        if (
            normalized_probability >= 70
            and ev >= 10
        ):
            return "Baixo"

        if (
            normalized_probability >= 55
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
        Calcula a média das odds disponíveis.

        Formato esperado:

            [
                {"odd": 2.10},
                {"odd": 2.15},
                {"odd": 2.05}
            ]
        """

        if not isinstance(bookmakers, list):
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
                odd = float(odd)
            except (TypeError, ValueError):
                continue

            if odd > 0:
                odds.append(odd)

        if not odds:
            return 0.0

        return round(
            sum(odds) / len(odds),
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
        Calcula a variação da melhor odd em relação
        à média do mercado.

        Exemplo:

            Melhor odd = 2.20
            Média = 2.00

            Variação = +10%
        """

        try:
            best_odd = float(best_odd)
            average_odd = float(average_odd)
        except (TypeError, ValueError):
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
        probability_available: bool = True,
    ) -> bool:
        """
        Determina se uma oportunidade é Value Bet.

        Para ser Value Bet:

        1. Deve existir probabilidade estimada independente;
        2. O EV deve atingir o limite mínimo.

        O padrão é EV >= 5%.
        """

        if not probability_available:
            return False

        try:
            ev = float(ev)
            minimum_ev = float(minimum_ev)
        except (TypeError, ValueError):
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
        Executa a análise quantitativa completa de um evento.

        O evento deve possuir uma estrutura semelhante a:

            {
                "home_team": "...",
                "away_team": "...",
                "best_odd": {
                    "odd": 2.10,
                    "outcome": "...",
                    "bookmaker": "...",
                    "market": "h2h"
                },
                "probability": 58.0
            }

        A probabilidade pode ser fornecida pelo Analyzer.

        Caso não exista uma probabilidade independente:

            - probability = 0
            - EV = 0
            - índice = 0
            - Value Bet = False
            - risco = Alto

        A probabilidade implícita continua disponível através
        do campo "implied_probability".
        """

        if not isinstance(event, dict):
            return {}

        # ------------------------------------------------------
        # MELHOR ODD
        # ------------------------------------------------------

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
                "implied_probability": 0.0,
                "probability": 0.0,
                "expected_value": 0.0,
                "oddreal_index": 0,
                "confidence_level": "Baixa",
                "average_odd": 0.0,
                "market_variation": 0.0,
                "risk": "Alto",
                "is_value_bet": False,
                "probability_available": False,
            }

        # ------------------------------------------------------
        # ODD
        # ------------------------------------------------------

        odd = best.get(
            "odd"
        )

        try:
            odd = float(odd)
        except (TypeError, ValueError):
            odd = 0.0

        if odd <= 0:

            return {
                **event,
                "odd": 0.0,
                "implied_probability": 0.0,
                "probability": 0.0,
                "expected_value": 0.0,
                "oddreal_index": 0,
                "confidence_level": "Baixa",
                "average_odd": 0.0,
                "market_variation": 0.0,
                "risk": "Alto",
                "is_value_bet": False,
                "probability_available": False,
            }

        # ------------------------------------------------------
        # PROBABILIDADE IMPLÍCITA
        # ------------------------------------------------------

        implied_probability = (
            self.implied_probability(
                odd
            )
        )

        # ------------------------------------------------------
        # PROBABILIDADE ESTIMADA
        # ------------------------------------------------------

        estimated_probability = (
            self.get_estimated_probability(
                event
            )
        )

        probability_available = (
            estimated_probability is not None
        )

        if probability_available:

            probability = (
                estimated_probability
                or 0.0
            )

            ev = self.expected_value(
                probability,
                odd,
            )

            index = self.oddreal_index(
                probability,
                ev,
            )

            confidence_level = (
                self.confidence_level(
                    index
                )
            )

            risk = self.risk_level(
                probability,
                ev,
            )

            value_bet = self.is_value_bet(
                ev,
                probability_available=True,
            )

        else:

            # --------------------------------------------------
            # SEM PROBABILIDADE INDEPENDENTE
            # --------------------------------------------------
            #
            # NÃO usamos a probabilidade implícita
            # para calcular EV.
            #
            # Isso evita o problema:
            #
            # (1 / odd × odd) - 1 = 0
            #
            # --------------------------------------------------

            probability = 0.0

            ev = 0.0

            index = 0

            confidence_level = "Baixa"

            risk = "Alto"

            value_bet = False

        # ------------------------------------------------------
        # MERCADO
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
        # RESULTADO
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

            # Probabilidade implícita do mercado.
            "implied_probability": (
                implied_probability
            ),

            # Probabilidade independente
            # utilizada pelo OddReal.
            "probability": round(
                probability,
                2,
            ),

            "probability_available": (
                probability_available
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


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

odds_engine = OddsEngine()
