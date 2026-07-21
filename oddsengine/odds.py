"""
OddReal 2.0
Módulo: oddsengine/odds.py

Motor principal de gerenciamento de odds.

Responsável por:
- Receber cotações
- Organizar mercados
- Normalizar dados
- Preparar cálculos de valor

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime


class OddsEngine:
    """
    Motor central de odds do OddReal.

    Controla as informações de mercado
    antes dos cálculos matemáticos.
    """


    def __init__(self):

        self.version = "2.0"
        self.created_at = datetime.now()



    # ==================================================
    # VALIDAÇÃO DE ODDS
    # ==================================================

    @staticmethod
    def validate_odds(
        odds: Dict[str, Any]
    ) -> bool:
        """
        Verifica se os dados de odds
        possuem estrutura válida.
        """

        if not odds:

            return False


        if not isinstance(
            odds,
            dict
        ):

            return False


        return True



    # ==================================================
    # NORMALIZAÇÃO DE MERCADOS
    # ==================================================

    def normalize_market(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Padroniza um mercado recebido
        de diferentes fontes.
        """

        return {

            "market":

                market.get(
                    "market",
                    "unknown"
                ),


            "outcomes":

                market.get(
                    "outcomes",
                    []
                ),


            "updated_at":

                datetime.now().isoformat()

        }



    # ==================================================
    # PROCESSAMENTO DE ODDS
    # ==================================================

    def process_odds(
        self,
        raw_odds: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recebe vários mercados
        e retorna formato padronizado.
        """

        processed = []


        for market in raw_odds:

            normalized = (
                self.normalize_market(
                    market
                )
            )


            processed.append(
                normalized
            )


        return processed



    # ==================================================
    # EXTRAÇÃO DE COTAÇÕES
    # ==================================================

    def extract_prices(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extrai odds de um mercado.
        """

        prices = {}


        outcomes = market.get(
            "outcomes",
            []
        )


        for outcome in outcomes:

            name = outcome.get(
                "name"
            )


            price = outcome.get(
                "price",
                0
            )


            if name:

                prices[name] = price



        return prices
          # ==================================================
    # CONVERSÃO DE ODD PARA PROBABILIDADE IMPLÍCITA
    # ==================================================

    def odds_to_probability(
        self,
        odd: float
    ) -> float:
        """
        Converte uma odd decimal em
        probabilidade implícita.

        Exemplo:
        Odd 2.00 = 50%
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
    # CONVERSÃO DE PROBABILIDADE PARA ODD JUSTA
    # ==================================================

    def probability_to_fair_odd(
        self,
        probability: float
    ) -> float:
        """
        Calcula a odd justa baseada
        na probabilidade estimada.
        """

        if probability <= 0:

            return 0


        fair_odd = (
            100 /
            probability
        )


        return round(
            fair_odd,
            2
        )



    # ==================================================
    # CÁLCULO DE MARGEM DA CASA
    # ==================================================

    def calculate_margin(
        self,
        odds: List[float]
    ) -> float:
        """
        Calcula o overround da casa.

        Quanto maior:
        maior a vantagem da casa.
        """

        if not odds:

            return 0


        probability_sum = 0


        for odd in odds:

            probability_sum += (
                1 / odd
            )



        margin = (
            probability_sum
            -
            1
        ) * 100


        return round(
            margin,
            2
        )



    # ==================================================
    # REMOÇÃO DA MARGEM DA CASA
    # ==================================================

    def remove_margin(
        self,
        odds: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Ajusta probabilidades retirando
        o efeito da margem da casa.
        """

        probabilities = {}


        total = 0


        for odd in odds.values():

            if odd > 0:

                total += (
                    1 / odd
                )



        if total == 0:

            return probabilities



        for name, odd in odds.items():

            if odd > 0:

                fair_probability = (

                    (
                        1 / odd
                    )
                    /
                    total

                ) * 100


                probabilities[name] = round(
                    fair_probability,
                    2
                )



        return probabilities



    # ==================================================
    # CÁLCULO DE ODD JUSTA DO MERCADO
    # ==================================================

    def fair_market_odds(
        self,
        probabilities: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Transforma probabilidades sem margem
        em odds justas.
        """

        fair_odds = {}


        for name, probability in probabilities.items():

            fair_odds[name] = (
                self.probability_to_fair_odd(
                    probability
                )
            )


        return fair_odds
      
    # ==================================================
    # COMPARAÇÃO PREVISÃO X MERCADO
    # ==================================================

    def compare_prediction_market(
        self,
        prediction_probability: float,
        market_odd: float
    ) -> Dict[str, float]:
        """
        Compara a probabilidade calculada pelo OddReal
        contra a probabilidade implícita da odd.

        Retorna:
        - probabilidade do modelo
        - probabilidade do mercado
        - diferença (edge)
        """

        market_probability = (
            self.odds_to_probability(
                market_odd
            )
        )


        edge = (
            prediction_probability
            -
            market_probability
        )


        return {

            "model_probability":
                round(
                    prediction_probability,
                    2
                ),

            "market_probability":
                round(
                    market_probability,
                    2
                ),

            "edge":
                round(
                    edge,
                    2
                )

        }



    # ==================================================
    # CÁLCULO DE VALOR ESPERADO
    # ==================================================

    def expected_value(
        self,
        probability: float,
        odd: float
    ) -> Dict[str, Any]:
        """
        Calcula o valor esperado matemático.

        Fórmula:
        (probabilidade x odd) - 1
        """

        if odd <= 0:

            return {

                "expected_value":
                    0,

                "has_value":
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

            "expected_value":
                round(
                    ev,
                    3
                ),

            "percentage":

                round(
                    ev * 100,
                    2
                ),

            "has_value":

                ev > 0

        }



    # ==================================================
    # CLASSIFICAÇÃO DE VALOR
    # ==================================================

    def classify_value(
        self,
        expected_value: float
    ) -> str:
        """
        Classifica a força da oportunidade.
        """

        if expected_value >= 0.15:

            return "strong_value"


        elif expected_value >= 0.05:

            return "positive_value"


        elif expected_value >= 0:

            return "small_value"


        else:

            return "no_value"



    # ==================================================
    # ANÁLISE COMPLETA DE UMA ODD
    # ==================================================

    def analyze_single_odd(
        self,
        market: str,
        prediction_probability: float,
        odd: float
    ) -> Dict[str, Any]:
        """
        Analisa uma oportunidade individual.
        """

        comparison = (
            self.compare_prediction_market(
                prediction_probability,
                odd
            )
        )


        value = (
            self.expected_value(
                prediction_probability,
                odd
            )
        )


        classification = (
            self.classify_value(
                value["expected_value"]
            )
        )


        return {

            "market":
                market,

            "odd":
                odd,

            "comparison":
                comparison,

            "value":
                value,

            "classification":
                classification

        }



    # ==================================================
    # ANÁLISE DE MÚLTIPLAS ODDS
    # ==================================================

    def analyze_markets(
        self,
        predictions: Dict[str, float],
        odds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Analisa vários mercados
        comparando modelo e casa.
        """

        results = []


        for market, probability in predictions.items():

            odd = odds.get(
                market,
                0
            )


            if odd <= 0:

                continue


            analysis = (
                self.analyze_single_odd(
                    market,
                    probability,
                    odd
                )
            )


            results.append(
                analysis
            )


        return results
          # ==================================================
    # SCORE DE OPORTUNIDADE
    # ==================================================

    def opportunity_score(
        self,
        edge: float,
        expected_value: float,
        confidence: float = 0
    ) -> float:
        """
        Cria uma pontuação geral da oportunidade.

        Considera:
        - diferença para o mercado
        - valor esperado
        - confiança do modelo
        """

        score = (

            (edge * 0.4)

            +

            (expected_value * 100 * 0.4)

            +

            (confidence * 0.2)

        )


        return round(
            score,
            2
        )



    # ==================================================
    # RANKING DE OPORTUNIDADES
    # ==================================================

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ordena oportunidades pelo melhor valor.
        """

        for item in opportunities:

            edge = (
                item
                .get(
                    "comparison",
                    {}
                )
                .get(
                    "edge",
                    0
                )
            )


            ev = (
                item
                .get(
                    "value",
                    {}
                )
                .get(
                    "expected_value",
                    0
                )
            )


            item["opportunity_score"] = (
                self.opportunity_score(
                    edge,
                    ev
                )
            )


        opportunities.sort(

            key=lambda x:
            x.get(
                "opportunity_score",
                0
            ),

            reverse=True

        )


        return opportunities



    # ==================================================
    # FILTRO DE VALUE BETS
    # ==================================================

    def filter_value_bets(
        self,
        opportunities: List[Dict[str, Any]],
        minimum_ev: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Retorna apenas apostas
        com valor esperado positivo.
        """

        value_bets = []


        for item in opportunities:

            ev = (

                item
                .get(
                    "value",
                    {}
                )
                .get(
                    "expected_value",
                    0
                )

            )


            if ev >= minimum_ev:

                value_bets.append(
                    item
                )


        return self.rank_opportunities(
            value_bets
        )



    # ==================================================
    # ANÁLISE DE RISCO DA ODD
    # ==================================================

    def risk_assessment(
        self,
        probability: float,
        odd: float
    ) -> Dict[str, Any]:
        """
        Avalia risco baseado na relação
        probabilidade x retorno.
        """

        implied = (
            self.odds_to_probability(
                odd
            )
        )


        difference = abs(
            probability
            -
            implied
        )


        if difference >= 20:

            risk = "high"


        elif difference >= 10:

            risk = "medium"


        else:

            risk = "low"



        return {

            "risk_level":
                risk,

            "probability_difference":
                round(
                    difference,
                    2
                )

        }



    # ==================================================
    # RESUMO DE MERCADO
    # ==================================================

    def market_report(
        self,
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cria relatório resumido
        das oportunidades.
        """

        ranked = self.rank_opportunities(
            analyses
        )


        return {

            "total_markets":
                len(ranked),

            "best_opportunities":
                ranked[:5],

            "generated_at":
                datetime.now().isoformat()

        }
          # ==================================================
    # INTEGRAÇÃO COM MOTOR DE PREVISÃO
    # ==================================================

    def compare_with_prediction_engine(
        self,
        prediction_data: Dict[str, Any],
        market_odds: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Cruza previsões do OddReal
        com odds disponíveis no mercado.

        Fluxo:

        PredictionEngine
              ↓
        OddsEngine
              ↓
        Value Analysis
        """

        probabilities = (
            prediction_data
            .get(
                "probabilities",
                {}
            )
        )


        analysis = (
            self.analyze_markets(
                probabilities,
                market_odds
            )
        )


        value_bets = (
            self.filter_value_bets(
                analysis
            )
        )


        return {

            "all_markets":

                analysis,


            "value_bets":

                value_bets,


            "market_report":

                self.market_report(
                    analysis
                )

        }



    # ==================================================
    # PROCESSAMENTO DE ODDS DA API
    # ==================================================

    def process_api_response(
        self,
        api_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara dados recebidos
        da The Odds API.

        Converte diferentes formatos
        para o padrão interno.
        """

        result = {

            "event":
                api_data.get(
                    "event",
                    ""
                ),


            "markets":
                []

        }


        bookmakers = (
            api_data
            .get(
                "bookmakers",
                []
            )
        )


        for bookmaker in bookmakers:

            for market in bookmaker.get(
                "markets",
                []
            ):

                normalized = (
                    self.normalize_market(
                        market
                    )
                )


                result["markets"].append(
                    normalized
                )


        return result



    # ==================================================
    # CONSOLIDAÇÃO DE MERCADOS
    # ==================================================

    def merge_markets(
        self,
        markets: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Junta mercados semelhantes
        em uma estrutura única.
        """

        merged = {}


        for market in markets:

            prices = (
                self.extract_prices(
                    market
                )
            )


            for name, price in prices.items():

                if name not in merged:

                    merged[name] = price


                else:

                    # Mantém a melhor odd encontrada

                    if price > merged[name]:

                        merged[name] = price



        return merged



    # ==================================================
    # MELHOR ODD DISPONÍVEL
    # ==================================================

    def find_best_odds(
        self,
        bookmakers: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Busca a maior cotação
        entre diferentes casas.
        """

        best = {}


        for bookmaker in bookmakers:

            markets = bookmaker.get(
                "markets",
                []
            )


            for market in markets:

                prices = (
                    self.extract_prices(
                        market
                    )
                )


                for name, odd in prices.items():

                    if (
                        name not in best
                        or
                        odd > best[name]
                    ):
    

                        best[name] = odd



        return best
          # ==================================================
    # GERADOR DE RELATÓRIO FINAL DE VALOR
    # ==================================================

    def generate_value_report(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria relatório final das oportunidades.

        Formato preparado para:
        - Streamlit
        - Dashboard
        - Histórico de análises
        """

        value_bets = (
            analysis
            .get(
                "value_bets",
                []
            )
        )


        strong_values = []


        for bet in value_bets:

            classification = (
                bet
                .get(
                    "classification",
                    ""
                )
            )


            if classification == "strong_value":

                strong_values.append(
                    bet
                )



        return {

            "total_opportunities":
                len(
                    value_bets
                ),

            "strong_opportunities":
                strong_values,

            "all_value_bets":
                value_bets,

            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # ANÁLISE COMPLETA DO MERCADO
    # ==================================================

    def run_odds_analysis(
        self,
        prediction_data: Dict[str, Any],
        odds_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Executa o fluxo completo do OddsEngine.

        Entrada:

        PredictionEngine
              +
        Odds mercado

        Saída:

        Value Bets classificadas
        """

        comparison = (
            self.compare_with_prediction_engine(
                prediction_data,
                odds_data
            )
        )


        report = (
            self.generate_value_report(
                comparison
            )
        )


        return {

            "status":
                "success",

            "comparison":
                comparison,

            "report":
                report,

            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # HISTÓRICO DE ANÁLISES
    # ==================================================

    def create_history_record(
        self,
        event: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria registro para histórico
        de análises realizadas.
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
        Retorna informações do OddsEngine.
        """

        return {

            "module":
                "oddsengine",

            "class":
                "OddsEngine",

            "version":
                self.version,

            "initialized":
                True,

            "created_at":
                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO MOTOR DE ODDS
# ======================================================

odds_engine = OddsEngine()
      
