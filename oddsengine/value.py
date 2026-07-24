"""
OddReal 2.0
Módulo: oddsengine/value.py

Motor de análise de Value Bets.

Responsável por:
- Classificação de oportunidades
- Score de entrada
- Avaliação de risco
- Ranking de apostas

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime



class ValueEngine:
    """
    Motor de decisão de valor matemático.
    """


    def __init__(self):

        self.version = "2.0"

        self.created_at = datetime.now()


        self.levels = {

            "premium":
                85,

            "strong":
                70,

            "moderate":
                50,

            "avoid":
                0

        }



    # ==================================================
    # VALIDAÇÃO DE OPORTUNIDADE
    # ==================================================

    def validate_opportunity(
        self,
        opportunity: Dict[str, Any]
    ) -> bool:
        """
        Verifica se uma oportunidade
        possui dados mínimos.
        """

        if not opportunity:

            return False


        required = [

            "probability",

            "odd"

        ]


        for field in required:

            if field not in opportunity:

                return False


        return True



    # ==================================================
    # CÁLCULO DE EDGE
    # ==================================================

    def calculate_edge(
        self,
        probability: float,
        market_probability: float
    ) -> float:
        """
        Calcula vantagem sobre o mercado.
        """

        return round(

            probability
            -
            market_probability,

            2

        )



    # ==================================================
    # CÁLCULO DE EV
    # ==================================================

    def calculate_ev(
        self,
        probability: float,
        odd: float
    ) -> float:
        """
        Calcula valor esperado.
        """

        if odd <= 0:

            return 0


        ev = (

            (
                probability
                /
                100
            )
            *
            odd

        ) - 1


        return round(
            ev * 100,
            2
        )
          # ==================================================
    # SCORE DE OPORTUNIDADE
    # ==================================================

    def calculate_score(
        self,
        edge: float,
        ev: float,
        confidence: float,
        risk: float = 0
    ) -> float:
        """
        Calcula nota geral da oportunidade.

        Considera:

        - Edge
        - Valor esperado
        - Confiança
        - Risco
        """

        score = (

            (edge * 0.35)

            +

            (ev * 0.35)

            +

            (confidence * 0.25)

            -

            (risk * 0.05)

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
    # ÍNDICE DE CONFIANÇA
    # ==================================================

    def calculate_confidence(
        self,
        probability: float,
        sample_size: int = 0,
        data_quality: float = 0
    ) -> float:
        """
        Calcula confiança da análise.

        Fatores:
        - probabilidade estimada
        - quantidade de dados
        - qualidade dos dados
        """

        probability_factor = (
            probability
            *
            0.5
        )


        sample_factor = min(

            sample_size
            *
            2,

            25

        )


        quality_factor = (

            data_quality
            *
            0.25

        )


        confidence = (

            probability_factor

            +

            sample_factor

            +

            quality_factor

        )


        return round(

            min(
                confidence,
                100
            ),

            2

        )



    # ==================================================
    # AVALIAÇÃO DE RISCO
    # ==================================================

    def calculate_risk(
        self,
        probability: float,
        odd: float
    ) -> float:
        """
        Mede risco matemático.

        Odds muito altas e baixa
        probabilidade aumentam risco.
        """

        if odd <= 0:

            return 100



        implied = (
            1 / odd
        ) * 100



        difference = abs(

            probability
            -
            implied

        )


        risk = (

            difference
            *
            2

        )


        return round(

            min(
                risk,
                100
            ),

            2

        )



    # ==================================================
    # CLASSIFICAÇÃO DA OPORTUNIDADE
    # ==================================================

    def classify_score(
        self,
        score: float
    ) -> str:
        """
        Transforma nota em categoria.
        """

        if score >= self.levels["premium"]:

            return "premium"



        elif score >= self.levels["strong"]:

            return "strong"



        elif score >= self.levels["moderate"]:

            return "moderate"



        else:

            return "avoid"
              # ==================================================
    # ANÁLISE COMPLETA DE OPORTUNIDADE
    # ==================================================

    def analyze_opportunity(
        self,
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa uma entrada completa.

        Entrada esperada:

        {
            "market": "Over 2.5",
            "probability": 65,
            "market_probability": 55,
            "odd": 1.90
        }
        """

        if not self.validate_opportunity(
            opportunity
        ):

            return {

                "status":
                    "invalid"

            }



        probability = (
            opportunity
            .get(
                "probability",
                0
            )
        )


        odd = (
            opportunity
            .get(
                "odd",
                0
            )
        )


        market_probability = (
            opportunity
            .get(
                "market_probability",
                0
            )
        )


        edge = (
            self.calculate_edge(
                probability,
                market_probability
            )
        )


        ev = (
            self.calculate_ev(
                probability,
                odd
            )
        )


        confidence = (
            self.calculate_confidence(
                probability,
                opportunity.get(
                    "sample_size",
                    0
                ),
                opportunity.get(
                    "data_quality",
                    0
                )
            )
        )


        risk = (
            self.calculate_risk(
                probability,
                odd
            )
        )


        score = (
            self.calculate_score(
                edge,
                ev,
                confidence,
                risk
            )
        )


        classification = (
            self.classify_score(
                score
            )
        )


        return {

            "status":
                "success",

            "market":
                opportunity.get(
                    "market",
                    ""
                ),

            "odd":
                odd,

            "probability":
                probability,

            "edge":
                edge,

            "expected_value":
                ev,

            "confidence":
                confidence,

            "risk":
                risk,

            "score":
                score,

            "classification":
                classification

        }



    # ==================================================
    # GERAÇÃO DE SINAL
    # ==================================================

    def generate_signal(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforma análise matemática
        em sinal operacional.
        """

        classification = (
            analysis.get(
                "classification",
                "avoid"
            )
        )


        signals = {

            "premium":
                "ENTER",

            "strong":
                "ENTER",

            "moderate":
                "WATCH",

            "avoid":
                "PASS"

        }


        return {

            "action":
                signals.get(
                    classification,
                    "PASS"
                ),


            "level":
                classification,


            "score":
                analysis.get(
                    "score",
                    0
                )

        }



    # ==================================================
    # EXPLICAÇÃO AUTOMÁTICA
    # ==================================================

    def explain_value(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Gera justificativas da oportunidade.
        """

        reasons = []


        if analysis.get(
            "edge",
            0
        ) > 5:

            reasons.append(
                "Modelo apresenta vantagem sobre o mercado"
            )


        if analysis.get(
            "expected_value",
            0
        ) > 5:

            reasons.append(
                "Valor esperado positivo"
            )


        if analysis.get(
            "confidence",
            0
        ) >= 70:

            reasons.append(
                "Alta confiança estatística"
            )


        if analysis.get(
            "risk",
            100
        ) > 70:

            reasons.append(
                "Atenção ao risco elevado"
            )


        return reasons
          # ==================================================
    # RANKING DE OPORTUNIDADES
    # ==================================================

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ordena oportunidades pela maior pontuação.
        """

        ranked = []


        for item in opportunities:

            analysis = (
                self.analyze_opportunity(
                    item
                )
            )


            if analysis.get(
                "status"
            ) == "success":

                ranked.append(
                    analysis
                )



        ranked.sort(

            key=lambda x:
                x.get(
                    "score",
                    0
                ),

            reverse=True

        )


        return ranked



    # ==================================================
    # FILTRO POR CLASSIFICAÇÃO
    # ==================================================

    def filter_by_level(
        self,
        opportunities: List[Dict[str, Any]],
        level: str
    ) -> List[Dict[str, Any]]:
        """
        Filtra oportunidades por categoria.

        Exemplos:
        premium
        strong
        moderate
        """

        result = []


        for item in opportunities:

            if (
                item.get(
                    "classification"
                )
                ==
                level
            ):

                result.append(
                    item
                )


        return result



    # ==================================================
    # MELHORES ENTRADAS
    # ==================================================

    def best_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna as melhores oportunidades.
        """

        ranked = (
            self.rank_opportunities(
                opportunities
            )
        )


        return ranked[:limit]



    # ==================================================
    # FILTRO DE ENTRADAS ACEITÁVEIS
    # ==================================================

    def filter_entries(
        self,
        opportunities: List[Dict[str, Any]],
        minimum_score: float = 70
    ) -> List[Dict[str, Any]]:
        """
        Mantém somente entradas
        acima da nota mínima.
        """

        approved = []


        ranked = (
            self.rank_opportunities(
                opportunities
            )
        )


        for item in ranked:

            if (
                item.get(
                    "score",
                    0
                )
                >=
                minimum_score
            ):

                approved.append(
                    item
                )


        return approved



    # ==================================================
    # COMPARAÇÃO ENTRE OPORTUNIDADES
    # ==================================================

    def compare_opportunities(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara duas entradas.
        """

        first_score = (
            first.get(
                "score",
                0
            )
        )


        second_score = (
            second.get(
                "score",
                0
            )
        )


        if first_score > second_score:

            winner = "first"


        elif second_score > first_score:

            winner = "second"


        else:

            winner = "equal"



        return {

            "winner":
                winner,

            "difference":
                round(
                    abs(
                        first_score
                        -
                        second_score
                    ),
                    2
                )

        }
          # ==================================================
    # CÁLCULO DE EXPOSIÇÃO
    # ==================================================

    def calculate_exposure(
        self,
        opportunities: List[Dict[str, Any]],
        stake_percentage: float = 1
    ) -> float:
        """
        Calcula exposição total de uma lista
        de oportunidades.
        """

        if not opportunities:

            return 0



        exposure = (

            len(opportunities)
            *
            stake_percentage

        )


        return round(
            exposure,
            2
        )



    # ==================================================
    # DIVERSIFICAÇÃO DE ENTRADAS
    # ==================================================

    def diversify_entries(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, List]:
        """
        Separa oportunidades por categoria
        de mercado.
        """

        categories = {}


        for item in opportunities:

            market = (
                item.get(
                    "market",
                    "unknown"
                )
            )


            if market not in categories:

                categories[market] = []



            categories[market].append(
                item
            )



        return categories



    # ==================================================
    # LIMITE DE RISCO
    # ==================================================

    def risk_limit_filter(
        self,
        opportunities: List[Dict[str, Any]],
        maximum_risk: float = 50
    ) -> List[Dict[str, Any]]:
        """
        Remove oportunidades com risco elevado.
        """

        filtered = []


        for item in opportunities:

            risk = (
                item.get(
                    "risk",
                    100
                )
            )


            if risk <= maximum_risk:

                filtered.append(
                    item
                )


        return filtered



    # ==================================================
    # SELEÇÃO FINAL DE ENTRADAS
    # ==================================================

    def select_final_entries(
        self,
        opportunities: List[Dict[str, Any]],
        max_entries: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Escolhe entradas finais combinando:

        - Score
        - Risco
        - Classificação
        """

        filtered = (
            self.risk_limit_filter(
                opportunities
            )
        )


        ranked = (
            self.rank_opportunities(
                filtered
            )
        )


        final = []


        for item in ranked:

            signal = (
                self.generate_signal(
                    item
                )
            )


            if signal["action"] == "ENTER":

                final.append(
                    item
                )


            if len(final) >= max_entries:

                break



        return final



    # ==================================================
    # RESUMO DE ESTRATÉGIA
    # ==================================================

    def strategy_summary(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gera resumo da estratégia.
        """

        ranked = (
            self.rank_opportunities(
                opportunities
            )
        )


        return {

            "total_analyzed":

                len(
                    opportunities
                ),


            "approved":

                len(
                    self.filter_entries(
                        opportunities
                    )
                ),


            "top_entries":

                ranked[:5],


            "generated_at":

                datetime.now().isoformat()

        }
          # ==================================================
    # RELATÓRIO FINAL DE VALUE BET
    # ==================================================

    def generate_value_report(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gera relatório completo de oportunidades.
        """

        ranked = (
            self.rank_opportunities(
                opportunities
            )
        )


        premium = (
            self.filter_by_level(
                ranked,
                "premium"
            )
        )


        strong = (
            self.filter_by_level(
                ranked,
                "strong"
            )
        )


        moderate = (
            self.filter_by_level(
                ranked,
                "moderate"
            )
        )


        return {

            "total":

                len(
                    ranked
                ),


            "premium":

                premium,


            "strong":

                strong,


            "moderate":

                moderate,


            "best":

                ranked[:10],


            "generated_at":

                datetime.now().isoformat()

        }



    # ==================================================
    # PIPELINE COMPLETO DE VALUE
    # ==================================================

    def run_analysis(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa todo o fluxo do ValueEngine.

        Entrada:
        Lista de oportunidades

        Saída:
        Value Bets classificadas
        """

        analyzed = (
            self.rank_opportunities(
                opportunities
            )
        )


        final_entries = (
            self.select_final_entries(
                analyzed
            )
        )


        report = (
            self.generate_value_report(
                analyzed
            )
        )


        return {

            "status":

                "success",


            "analyzed":

                analyzed,


            "final_entries":

                final_entries,


            "report":

                report

        }



    # ==================================================
    # HISTÓRICO DE DECISÃO
    # ==================================================

    def create_record(
        self,
        event: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria registro para histórico.
        """

        return {

            "event":

                event,


            "analysis":

                analysis,


            "created_at":

                datetime.now().isoformat()

        }



    # ==================================================
    # STATUS DO MOTOR
    # ==================================================

    def engine_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do ValueEngine.
        """

        return {

            "module":

                "oddsengine.value",


            "class":

                "ValueEngine",


            "version":

                self.version,


            "initialized":

                True,


            "created_at":

                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO VALUE ENGINE
# ======================================================

value_engine = ValueEngine()
