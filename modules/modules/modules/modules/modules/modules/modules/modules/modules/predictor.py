"""
OddReal 2.0
Módulo: predictions.py

Motor de previsões estatísticas.

Responsável por:
- Probabilidade de resultados
- Projeções de mercados
- Confiança das previsões
- Ranking de oportunidades

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime


class PredictionEngine:
    """
    Motor preditivo do OddReal.

    Usa dados estatísticos e análises
    para gerar previsões.
    """


    def __init__(self):

        self.version = "2.0"
        self.created_at = datetime.now()



    # ==================================================
    # VALIDAÇÃO DE DADOS
    # ==================================================

    @staticmethod
    def validate_data(
        data: Dict[str, Any]
    ) -> bool:
        """
        Verifica se os dados são suficientes.
        """

        if not data:
            return False


        required = [
            "home",
            "away"
        ]


        for item in required:

            if item not in data:
                return False


        return True



    # ==================================================
    # EXTRAÇÃO DE INDICADORES
    # ==================================================

    def extract_team_metrics(
        self,
        team: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extrai indicadores principais.
        """

        return {

            "strength":
                team
                .get(
                    "strength",
                    {}
                )
                .get(
                    "strength_rating",
                    0
                ),


            "attack":
                team
                .get(
                    "attack",
                    {}
                )
                .get(
                    "attack_index",
                    0
                ),


            "defense":
                team
                .get(
                    "defense",
                    {}
                )
                .get(
                    "defense_index",
                    0
                ),


            "form":
                team
                .get(
                    "form",
                    {}
                )
                .get(
                    "form_percentage",
                    0
                )

        }



    # ==================================================
    # PROBABILIDADE DE VITÓRIA
    # ==================================================

    def calculate_win_probability(
        self,
        home_metrics: Dict[str, float],
        away_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula probabilidade estimada
        de vitória de cada equipe.
        """

        home_score = (

            home_metrics["strength"] * 0.5

            +

            home_metrics["attack"] * 0.2

            +

            home_metrics["form"] * 0.3

        )


        away_score = (

            away_metrics["strength"] * 0.5

            +

            away_metrics["attack"] * 0.2

            +

            away_metrics["form"] * 0.3

        )


        total = (
            home_score
            +
            away_score
        )


        if total == 0:

            return {

                "home_win":
                    0,

                "away_win":
                    0,

                "draw":
                    0

            }



        home_probability = (
            home_score
            /
            total
        ) * 100


        away_probability = (
            away_score
            /
            total
        ) * 100



        draw_probability = max(
            0,
            100 -
            (
                home_probability
                +
                away_probability
            )
        )


        return {

            "home_win":
                round(
                    home_probability,
                    2
                ),


            "away_win":
                round(
                    away_probability,
                    2
                ),


            "draw":
                round(
                    draw_probability,
                    2
                )

      }
          # ==================================================
    # PREVISÃO DE GOLS
    # ==================================================

    def predict_goals(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Estima expectativa de gols
        de cada equipe.

        Baseado em:
        - ataque
        - defesa adversária
        - força geral
        """

        home_attack = (
            home
            .get(
                "attack",
                {}
            )
            .get(
                "attack_index",
                0
            )
        )


        away_attack = (
            away
            .get(
                "attack",
                {}
            )
            .get(
                "attack_index",
                0
            )
        )


        home_defense = (
            home
            .get(
                "defense",
                {}
            )
            .get(
                "defense_index",
                0
            )
        )


        away_defense = (
            away
            .get(
                "defense",
                {}
            )
            .get(
                "defense_index",
                0
            )
        )


        home_expected = (

            (
                home_attack
                +
                (100 - away_defense)
            )
            /
            100

        ) * 1.5



        away_expected = (

            (
                away_attack
                +
                (100 - home_defense)
            )
            /
            100

        ) * 1.5



        return {

            "home_expected_goals":
                round(
                    min(
                        home_expected,
                        5
                    ),
                    2
                ),


            "away_expected_goals":
                round(
                    min(
                        away_expected,
                        5
                    ),
                    2
                ),


            "total_expected_goals":
                round(
                    home_expected
                    +
                    away_expected,
                    2
                )

        }



    # ==================================================
    # PROBABILIDADE OVER / UNDER
    # ==================================================

    def predict_over_under(
        self,
        expected_goals: float
    ) -> Dict[str, Any]:
        """
        Calcula tendência de gols
        usando gols esperados.
        """

        markets = {

            "over_1_5": 0,

            "over_2_5": 0,

            "over_3_5": 0,

            "under_2_5": 0

        }


        if expected_goals >= 1.5:

            markets["over_1_5"] = 80

        else:

            markets["over_1_5"] = 35



        if expected_goals >= 2.5:

            markets["over_2_5"] = 70

        else:

            markets["over_2_5"] = 40



        if expected_goals >= 3.5:

            markets["over_3_5"] = 60

        else:

            markets["over_3_5"] = 45



        if expected_goals <= 2.5:

            markets["under_2_5"] = 65

        else:

            markets["under_2_5"] = 30



        return markets



    # ==================================================
    # PROBABILIDADE AMBAS MARCAM
    # ==================================================

    def predict_btts(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Estima chance de ambas equipes
        marcarem.
        """

        home_attack = (
            home
            .get(
                "attack",
                {}
            )
            .get(
                "attack_index",
                0
            )
        )


        away_attack = (
            away
            .get(
                "attack",
                {}
            )
            .get(
                "attack_index",
                0
            )
        )


        probability = (
            (
                home_attack
                +
                away_attack
            )
            /
            2
        )


        probability = min(
            max(
                probability,
                0
            ),
            100
        )


        return {

            "btts_yes":
                round(
                    probability,
                    2
                ),


            "btts_no":
                round(
                    100 - probability,
                    2
                )

        }



    # ==================================================
    # PLACAR PROVÁVEL
    # ==================================================

    def probable_score(
        self,
        goal_prediction: Dict[str, float]
    ) -> Dict[str, int]:
        """
        Converte expectativa de gols
        em placar provável.
        """

        home_goals = round(
            goal_prediction
            .get(
                "home_expected_goals",
                0
            )
        )


        away_goals = round(
            goal_prediction
            .get(
                "away_expected_goals",
                0
            )
        )


        return {

            "home_score":
                min(
                    home_goals,
                    5
                ),

            "away_score":
                min(
                    away_goals,
                    5
                )

      }
          # ==================================================
    # AJUSTE POR MANDO DE CAMPO
    # ==================================================

    def apply_home_advantage(
        self,
        probability: Dict[str, float],
        advantage: float = 5
    ) -> Dict[str, float]:
        """
        Aplica ajuste estatístico pelo mando de campo.

        O valor padrão adiciona uma pequena vantagem
        ao mandante sem distorcer a previsão.
        """

        home = probability.get(
            "home_win",
            0
        )

        away = probability.get(
            "away_win",
            0
        )


        home += advantage

        away -= advantage


        home = max(
            min(home, 100),
            0
        )

        away = max(
            min(away, 100),
            0
        )


        total = (
            home
            +
            away
        )


        if total > 100:

            factor = 100 / total

            home *= factor

            away *= factor



        draw = max(
            0,
            100 - home - away
        )


        return {

            "home_win":
                round(home, 2),

            "away_win":
                round(away, 2),

            "draw":
                round(draw, 2)

        }



    # ==================================================
    # PESO DA FORMA RECENTE
    # ==================================================

    def calculate_form_weight(
        self,
        team: Dict[str, Any]
    ) -> float:
        """
        Calcula influência da fase recente.

        Times em boa fase recebem maior peso.
        """

        form = (
            team
            .get(
                "form",
                {}
            )
            .get(
                "form_percentage",
                0
            )
        )


        if form >= 80:

            return 1.20


        elif form >= 60:

            return 1.10


        elif form >= 40:

            return 1.00


        else:

            return 0.90



    # ==================================================
    # CORREÇÃO DE PROBABILIDADES
    # ==================================================

    def adjust_probability(
        self,
        probability: Dict[str, float],
        home_weight: float,
        away_weight: float
    ) -> Dict[str, float]:
        """
        Ajusta probabilidades utilizando
        momento das equipes.
        """

        home = (
            probability
            .get(
                "home_win",
                0
            )
            *
            home_weight
        )


        away = (
            probability
            .get(
                "away_win",
                0
            )
            *
            away_weight
        )


        draw = (
            probability
            .get(
                "draw",
                0
            )
        )


        total = (
            home
            +
            away
            +
            draw
        )


        if total == 0:

            return probability



        return {

            "home_win":
                round(
                    (home / total) * 100,
                    2
                ),

            "away_win":
                round(
                    (away / total) * 100,
                    2
                ),

            "draw":
                round(
                    (draw / total) * 100,
                    2
                )

        }



    # ==================================================
    # ÍNDICE DE CONFIANÇA DA PREVISÃO
    # ==================================================

    def prediction_confidence(
        self,
        probabilities: Dict[str, float],
        sample_size: int,
        consistency: float
    ) -> Dict[str, Any]:
        """
        Mede confiança geral da previsão.

        Considera:
        - diferença entre probabilidades
        - quantidade de dados
        - regularidade
        """

        values = [

            probabilities.get(
                "home_win",
                0
            ),

            probabilities.get(
                "away_win",
                0
            ),

            probabilities.get(
                "draw",
                0
            )

        ]


        maximum = max(
            values
        )


        sample_factor = min(
            sample_size * 8,
            100
        )


        confidence = (

            maximum * 0.5

            +

            sample_factor * 0.25

            +

            consistency * 0.25

        )


        confidence = min(
            round(
                confidence,
                2
            ),
            100
        )


        if confidence >= 75:

            level = "high"


        elif confidence >= 50:

            level = "medium"


        else:

            level = "low"



        return {

            "confidence":
                confidence,

            "level":
                level

        }
          # ==================================================
    # GERAÇÃO DE MERCADOS
    # ==================================================

    def generate_markets(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera uma visão geral dos mercados
        possíveis da partida.
        """

        goals = self.predict_goals(
            home,
            away
        )


        over_under = self.predict_over_under(
            goals["total_expected_goals"]
        )


        btts = self.predict_btts(
            home,
            away
        )


        score = self.probable_score(
            goals
        )


        return {

            "goals_prediction":
                goals,

            "over_under":
                over_under,

            "btts":
                btts,

            "probable_score":
                score

        }



    # ==================================================
    # IDENTIFICAÇÃO DE MELHORES MERCADOS
    # ==================================================

    def find_best_markets(
        self,
        markets: Dict[str, Any],
        minimum: float = 65
    ) -> List[Dict[str, Any]]:
        """
        Seleciona mercados com maior suporte
        estatístico.
        """

        opportunities = []


        over_under = markets.get(
            "over_under",
            {}
        )


        for market, probability in over_under.items():

            if probability >= minimum:

                opportunities.append(

                    {

                        "market":
                            market,

                        "probability":
                            probability

                    }

                )



        btts = markets.get(
            "btts",
            {}
        )


        for market, probability in btts.items():

            if probability >= minimum:

                opportunities.append(

                    {

                        "market":
                            market,

                        "probability":
                            probability

                    }

                )



        opportunities.sort(

            key=lambda x:
            x["probability"],

            reverse=True

        )


        return opportunities



    # ==================================================
    # CÁLCULO DE VALOR ESTATÍSTICO
    # ==================================================

    def calculate_value(
        self,
        probability: float,
        odd: float
    ) -> Dict[str, float]:
        """
        Calcula se existe valor matemático
        em uma odd oferecida.

        Valor esperado:
        (probabilidade x odd) - 1
        """

        if odd <= 0:

            return {

                "expected_value":
                    0,

                "has_value":
                    False

            }



        expected_value = (

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
                    expected_value,
                    3
                ),

            "has_value":
                expected_value > 0

        }



    # ==================================================
    # RANKING DE OPORTUNIDADES
    # ==================================================

    def rank_predictions(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Organiza previsões pela confiança.
        """

        ranked = sorted(

            opportunities,

            key=lambda item:
            item.get(
                "probability",
                0
            ),

            reverse=True

        )


        for index, item in enumerate(
            ranked,
            start=1
        ):

            item["rank"] = index



        return ranked



    # ==================================================
    # RESUMO DOS MERCADOS
    # ==================================================

    def market_summary(
        self,
        markets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria resumo compacto dos mercados.
        """

        best = self.find_best_markets(
            markets
        )


        return {

            "best_opportunities":
                self.rank_predictions(
                    best
                ),

            "total_markets":
                len(best),

            "generated_at":
                datetime.now().isoformat()

        }
          # ==================================================
    # PIPELINE COMPLETO DE PREVISÃO
    # ==================================================

    def run_prediction(
        self,
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa o fluxo completo de previsão.

        Processo:

        Dados estatísticos
              ↓
        Probabilidades
              ↓
        Ajustes
              ↓
        Mercados
              ↓
        Confiança
              ↓
        Relatório final
        """

        if not self.validate_data(
            match_data
        ):

            return {

                "status":
                    "error",

                "message":
                    "Dados insuficientes"

            }



        home = match_data["home"]

        away = match_data["away"]



        # Extrair métricas

        home_metrics = (
            self.extract_team_metrics(
                home
            )
        )


        away_metrics = (
            self.extract_team_metrics(
                away
            )
        )



        # Probabilidade inicial

        probabilities = (
            self.calculate_win_probability(
                home_metrics,
                away_metrics
            )
        )



        # Ajuste por mando

        probabilities = (
            self.apply_home_advantage(
                probabilities
            )
        )



        # Ajuste por forma

        home_weight = (
            self.calculate_form_weight(
                home
            )
        )


        away_weight = (
            self.calculate_form_weight(
                away
            )
        )


        probabilities = (
            self.adjust_probability(
                probabilities,
                home_weight,
                away_weight
            )
        )



        # Mercados

        markets = (
            self.generate_markets(
                home,
                away
            )
        )



        # Oportunidades

        opportunities = (
            self.find_best_markets(
                markets
            )
        )



        # Confiança

        consistency_home = (
            home
            .get(
                "consistency",
                {}
            )
            .get(
                "consistency_index",
                0
            )
        )


        consistency_away = (
            away
            .get(
                "consistency",
                {}
            )
            .get(
                "consistency_index",
                0
            )
        )


        average_consistency = (

            consistency_home
            +
            consistency_away

        ) / 2



        confidence = (
            self.prediction_confidence(
                probabilities,
                len(
                    home.get(
                        "form",
                        {}
                    )
                ),
                average_consistency
            )
        )



        return {

            "status":
                "success",


            "probabilities":
                probabilities,


            "markets":
                markets,


            "opportunities":
                opportunities,


            "confidence":
                confidence,


            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # ANÁLISE DE VÁRIAS PARTIDAS
    # ==================================================

    def predict_multiple(
        self,
        matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Executa previsões em lote.
        """

        predictions = []


        for match in matches:

            result = (
                self.run_prediction(
                    match
                )
            )


            predictions.append(
                result
            )


        return predictions



    # ==================================================
    # FILTRO DE MELHORES ENTRADAS
    # ==================================================

    def filter_best_predictions(
        self,
        predictions: List[Dict[str, Any]],
        minimum_confidence: float = 70
    ) -> List[Dict[str, Any]]:
        """
        Retorna apenas previsões
        com confiança acima do limite.
        """

        filtered = []


        for prediction in predictions:

            confidence = (

                prediction
                .get(
                    "confidence",
                    {}
                )
                .get(
                    "confidence",
                    0
                )

            )


            if confidence >= minimum_confidence:

                filtered.append(
                    prediction
                )


        return filtered
          # ==================================================
    # INTEGRAÇÃO COM ODDS
    # ==================================================

    def analyze_odds_value(
        self,
        predictions: Dict[str, Any],
        odds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Compara probabilidades calculadas
        com odds disponíveis no mercado.

        Identifica possíveis valores.
        """

        opportunities = []


        probability_map = {

            "home_win":
                predictions
                .get(
                    "probabilities",
                    {}
                )
                .get(
                    "home_win",
                    0
                ),

            "away_win":
                predictions
                .get(
                    "probabilities",
                    {}
                )
                .get(
                    "away_win",
                    0
                ),

            "draw":
                predictions
                .get(
                    "probabilities",
                    {}
                )
                .get(
                    "draw",
                    0
                )

        }


        for market, probability in probability_map.items():

            odd = odds.get(
                market,
                0
            )


            if odd <= 0:

                continue


            value = self.calculate_value(
                probability,
                odd
            )


            opportunities.append(

                {

                    "market":
                        market,

                    "probability":
                        probability,

                    "odd":
                        odd,

                    "expected_value":
                        value["expected_value"],

                    "has_value":
                        value["has_value"]

                }

            )


        return opportunities



    # ==================================================
    # RELATÓRIO FINAL DE PREVISÃO
    # ==================================================

    def create_prediction_report(
        self,
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria formato final para
        exibição no OddReal.
        """

        return {

            "match_probability":
                prediction
                .get(
                    "probabilities",
                    {}
                ),


            "main_markets":
                prediction
                .get(
                    "markets",
                    {}
                ),


            "best_opportunities":
                prediction
                .get(
                    "opportunities",
                    []
                ),


            "confidence":
                prediction
                .get(
                    "confidence",
                    {}
                ),


            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # STATUS DO MOTOR
    # ==================================================

    def engine_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do módulo.
        """

        return {

            "module":
                "predictions",

            "version":
                self.version,

            "initialized":
                True,

            "created_at":
                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO MOTOR PREDITIVO
# ======================================================

prediction_engine = PredictionEngine()
