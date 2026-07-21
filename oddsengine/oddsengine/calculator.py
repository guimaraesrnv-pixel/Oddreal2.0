"""
OddReal 2.0
Módulo: oddsengine/calculator.py

Calculadora matemática de odds.

Responsável por:
- Conversões matemáticas
- Probabilidades
- Odds justas
- Métricas de valor

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime


class OddsCalculator:
    """
    Motor matemático do OddsEngine.
    """


    def __init__(self):

        self.version = "2.0"
        self.created_at = datetime.now()



    # ==================================================
    # ODD PARA PROBABILIDADE
    # ==================================================

    def implied_probability(
        self,
        odd: float
    ) -> float:
        """
        Converte odd decimal em
        probabilidade implícita.
        """

        if odd <= 0:

            return 0


        probability = (
            1 / odd
        ) * 100


        return round(
            probability,
            2
        )



    # ==================================================
    # PROBABILIDADE PARA ODD
    # ==================================================

    def fair_odd(
        self,
        probability: float
    ) -> float:
        """
        Calcula odd justa.
        """

        if probability <= 0:

            return 0


        odd = (
            100 /
            probability
        )


        return round(
            odd,
            2
        )



    # ==================================================
    # NORMALIZAÇÃO DE PROBABILIDADE
    # ==================================================

    def normalize_probabilities(
        self,
        probabilities: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Ajusta probabilidades para somarem 100%.
        """

        total = sum(
            probabilities.values()
        )


        if total == 0:

            return probabilities



        normalized = {}


        for key, value in probabilities.items():

            normalized[key] = round(

                (
                    value
                    /
                    total
                )
                *
                100,

                2

            )


        return normalized
          # ==================================================
    # CÁLCULO DE MARGEM DA CASA
    # ==================================================

    def calculate_overround(
        self,
        odds: List[float]
    ) -> float:
        """
        Calcula a margem embutida
        pela casa de apostas.
        """

        if not odds:
            return 0


        total_probability = 0


        for odd in odds:

            if odd > 0:

                total_probability += (
                    1 / odd
                )



        margin = (
            total_probability - 1
        ) * 100


        return round(
            margin,
            2
        )



    # ==================================================
    # REMOVER MARGEM DA CASA
    # ==================================================

    def remove_bookmaker_margin(
        self,
        odds: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Remove o overround e retorna
        probabilidades ajustadas.
        """

        implied = {}


        total = 0


        for odd in odds.values():

            if odd > 0:

                total += (
                    1 / odd
                )



        if total == 0:

            return {}



        for name, odd in odds.items():

            implied[name] = round(

                (
                    (1 / odd)
                    /
                    total
                )
                *
                100,

                2

            )


        return implied



    # ==================================================
    # CÁLCULO DE EDGE
    # ==================================================

    def calculate_edge(
        self,
        model_probability: float,
        market_probability: float
    ) -> float:
        """
        Diferença entre modelo e mercado.
        """

        return round(
            model_probability
            -
            market_probability,
            2
        )
          # ==================================================
    # EXPECTED VALUE (VALOR ESPERADO)
    # ==================================================

    def expected_value(
        self,
        probability: float,
        odd: float
    ) -> Dict[str, Any]:
        """
        Calcula o valor esperado matemático.

        Fórmula:
        EV = (Probabilidade × Odd) - 1
        """

        if odd <= 0:

            return {

                "ev":
                    0,

                "percentage":
                    0,

                "positive":
                    False

            }



        ev = (

            (
                probability
                /
                100
            )
            *
            odd

        ) - 1



        return {

            "ev":
                round(
                    ev,
                    4
                ),

            "percentage":
                round(
                    ev * 100,
                    2
                ),

            "positive":
                ev > 0

        }



    # ==================================================
    # KELLY CRITERION
    # ==================================================

    def kelly_fraction(
        self,
        probability: float,
        odd: float
    ) -> float:
        """
        Calcula fração ideal de Kelly.

        Usado para gerenciamento
        matemático de banca.
        """

        if odd <= 1:

            return 0


        p = (
            probability
            /
            100
        )


        q = 1 - p


        b = odd - 1


        kelly = (

            (
                b * p
            )
            -
            q

        ) / b



        if kelly < 0:

            return 0



        return round(
            kelly * 100,
            2
        )



    # ==================================================
    # STAKE RECOMENDADA
    # ==================================================

    def recommended_stake(
        self,
        bankroll: float,
        kelly_percentage: float,
        fraction: float = 0.25
    ) -> float:
        """
        Calcula stake usando Kelly fracionado.

        Padrão:
        25% do Kelly completo.
        """

        if bankroll <= 0:

            return 0


        stake = (

            bankroll
            *
            (
                kelly_percentage
                /
                100
            )
            *
            fraction

        )


        return round(
            stake,
            2
        )



    # ==================================================
    # CLASSIFICAÇÃO DO VALOR
    # ==================================================

    def value_rating(
        self,
        ev: float
    ) -> str:
        """
        Classifica a força matemática
        da oportunidade.
        """

        if ev >= 0.15:

            return "excellent"


        elif ev >= 0.08:

            return "good"


        elif ev >= 0:

            return "weak"


        else:

            return "negative"
              # ==================================================
    # ODDS COMBINADAS
    # ==================================================

    def combined_odd(
        self,
        odds: List[float]
    ) -> float:
        """
        Calcula odd acumulada de múltiplos eventos.
        """

        if not odds:

            return 0


        result = 1


        for odd in odds:

            if odd <= 0:

                return 0


            result *= odd



        return round(
            result,
            2
        )



    # ==================================================
    # PROBABILIDADE COMBINADA
    # ==================================================

    def combined_probability(
        self,
        probabilities: List[float]
    ) -> float:
        """
        Calcula probabilidade conjunta
        de múltiplos eventos.
        """

        if not probabilities:

            return 0


        result = 1


        for probability in probabilities:

            result *= (
                probability
                /
                100
            )



        return round(
            result * 100,
            2
        )



    # ==================================================
    # VALOR ESPERADO DE COMBINADA
    # ==================================================

    def combined_expected_value(
        self,
        probabilities: List[float],
        odd: float
    ) -> Dict[str, Any]:
        """
        Calcula EV de uma aposta múltipla.
        """

        probability = (
            self.combined_probability(
                probabilities
            )
        )


        return self.expected_value(
            probability,
            odd
        )



    # ==================================================
    # CORREÇÃO DE CORRELAÇÃO
    # ==================================================

    def correlation_adjustment(
        self,
        probability: float,
        correlation_factor: float = 1.0
    ) -> float:
        """
        Ajusta probabilidade quando mercados
        possuem relação entre si.

        Exemplo:
        dois mercados do mesmo jogo.
        """

        adjusted = (

            probability
            *
            correlation_factor

        )


        return round(

            min(
                max(
                    adjusted,
                    0
                ),
                100
            ),

            2

        )



    # ==================================================
    # ANÁLISE DE COMBINAÇÃO
    # ==================================================

    def analyze_combination(
        self,
        selections: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Analisa uma múltipla completa.

        Recebe:

        [
            {
                "probability": 70,
                "odd": 1.80
            }
        ]

        """

        probabilities = []

        odds = []


        for item in selections:

            probabilities.append(

                item.get(
                    "probability",
                    0
                )

            )


            odds.append(

                item.get(
                    "odd",
                    0
                )

            )



        combined_odd = (
            self.combined_odd(
                odds
            )
        )


        combined_probability = (
            self.combined_probability(
                probabilities
            )
        )


        value = (
            self.expected_value(
                combined_probability,
                combined_odd
            )
        )


        return {

            "combined_odd":
                combined_odd,

            "combined_probability":
                combined_probability,

            "value":
                value

        }
          # ==================================================
    # ÍNDICE DE CONFIANÇA MATEMÁTICA
    # ==================================================

    def confidence_index(
        self,
        probability: float,
        edge: float,
        sample_size: int = 0
    ) -> float:
        """
        Calcula um índice matemático de confiança.

        Considera:
        - probabilidade estimada;
        - vantagem sobre o mercado;
        - quantidade de dados.
        """

        probability_score = (
            probability * 0.5
        )


        edge_score = (
            max(
                edge,
                0
            )
            *
            2
        )


        sample_score = min(
            sample_size * 2,
            20
        )


        confidence = (

            probability_score

            +

            edge_score

            +

            sample_score

        )


        return round(
            min(
                confidence,
                100
            ),
            2
        )



    # ==================================================
    # DISTÂNCIA ENTRE MODELO E MERCADO
    # ==================================================

    def market_gap(
        self,
        model_probability: float,
        market_probability: float
    ) -> Dict[str, float]:
        """
        Mede a diferença entre
        previsão própria e mercado.
        """

        gap = (

            model_probability
            -
            market_probability

        )


        absolute_gap = abs(
            gap
        )


        return {

            "gap":
                round(
                    gap,
                    2
                ),

            "absolute_gap":
                round(
                    absolute_gap,
                    2
                )

        }



    # ==================================================
    # PONTUAÇÃO GERAL DE OPORTUNIDADE
    # ==================================================

    def opportunity_score(
        self,
        ev: float,
        edge: float,
        confidence: float
    ) -> float:
        """
        Junta todas as métricas
        em uma pontuação única.
        """

        score = (

            (ev * 100 * 0.4)

            +

            (edge * 0.3)

            +

            (confidence * 0.3)

        )


        return round(
            min(
                max(
                    score,
                    0
                ),
                100
            ),
            2
        )



    # ==================================================
    # COMPARADOR DE MODELOS
    # ==================================================

    def compare_models(
        self,
        models: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compara diferentes modelos
        de previsão.

        Exemplo:
        estatístico,
        mercado,
        IA.
        """

        if not models:

            return {}



        average = (

            sum(
                models.values()
            )
            /
            len(
                models
            )

        )


        differences = {}


        for name, value in models.items():

            differences[name] = round(

                value
                -
                average,

                2

            )



        return {

            "average":
                round(
                    average,
                    2
                ),

            "differences":
                differences

        }



    # ==================================================
    # RESUMO MATEMÁTICO
    # ==================================================

    def mathematical_summary(
        self,
        probability: float,
        odd: float,
        sample_size: int = 0
    ) -> Dict[str, Any]:
        """
        Gera resumo completo
        de uma oportunidade.
        """

        market_probability = (
            self.implied_probability(
                odd
            )
        )


        edge = (
            self.calculate_edge(
                probability,
                market_probability
            )
        )


        value = (
            self.expected_value(
                probability,
                odd
            )
        )


        confidence = (
            self.confidence_index(
                probability,
                edge,
                sample_size
            )
        )


        score = (
            self.opportunity_score(
                value["ev"],
                edge,
                confidence
            )
        )


        return {

            "model_probability":
                probability,

            "market_probability":
                market_probability,

            "edge":
                edge,

            "expected_value":
                value,

            "confidence":
                confidence,

            "score":
                score

        }
          # ==================================================
    # RELATÓRIO FINAL MATEMÁTICO
    # ==================================================

    def generate_report(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera relatório final da análise matemática.
        """

        return {

            "analysis":
                analysis,

            "classification":
                self.value_rating(
                    analysis
                    .get(
                        "expected_value",
                        {}
                    )
                    .get(
                        "ev",
                        0
                    )
                ),

            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # ANÁLISE COMPLETA DE UMA OPORTUNIDADE
    # ==================================================

    def analyze_opportunity(
        self,
        probability: float,
        odd: float,
        sample_size: int = 0
    ) -> Dict[str, Any]:
        """
        Executa todos os cálculos
        necessários para uma entrada.
        """

        summary = (
            self.mathematical_summary(
                probability,
                odd,
                sample_size
            )
        )


        report = (
            self.generate_report(
                summary
            )
        )


        return {

            "status":
                "success",

            "summary":
                summary,

            "report":
                report

        }



    # ==================================================
    # VALIDAÇÃO DE ENTRADA
    # ==================================================

    def validate_input(
        self,
        probability: float,
        odd: float
    ) -> bool:
        """
        Valida dados recebidos.
        """

        if probability <= 0:

            return False


        if probability > 100:

            return False


        if odd <= 1:

            return False


        return True



    # ==================================================
    # STATUS DO MOTOR
    # ==================================================

    def engine_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do calculador.
        """

        return {

            "module":
                "oddsengine.calculator",

            "class":
                "OddsCalculator",

            "version":
                self.version,

            "initialized":
                True,

            "created_at":
                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO CALCULADOR
# ======================================================

odds_calculator = OddsCalculator()
      
