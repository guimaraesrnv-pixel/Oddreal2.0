"""
OddReal 2.0
Módulo: statistics.py

Responsável pelo processamento estatístico dos eventos esportivos.

Funções principais:
- Cálculo de médias
- Análise de desempenho
- Estatísticas ofensivas e defensivas
- Tendências recentes
- Normalização dos dados
- Preparação para modelos preditivos

Autor: OddReal Team
Versão: 2.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class StatisticsEngine:
    """
    Motor principal de estatísticas do OddReal.

    Este módulo recebe dados brutos provenientes
    da API e transforma em indicadores utilizáveis.
    """

    def __init__(self):
        self.version = "2.0"
        self.created_at = datetime.now()

    # ==================================================
    # MÉTODOS BÁSICOS DE VALIDAÇÃO
    # ==================================================

    @staticmethod
    def validate_data(data: Any) -> bool:
        """
        Verifica se os dados recebidos são válidos.
        """

        if data is None:
            return False

        if not isinstance(data, (dict, list)):
            return False

        return True


    # ==================================================
    # CÁLCULO DE MÉDIAS
    # ==================================================

    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """
        Calcula média simples de uma lista.
        """

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            2
        )


    @staticmethod
    def calculate_percentage(
        value: float,
        total: float
    ) -> float:
        """
        Calcula porcentagem.
        """

        if total == 0:
            return 0.0

        return round(
            (value / total) * 100,
            2
        )


    # ==================================================
    # ESTATÍSTICAS DE GOLS
    # ==================================================

    def goals_average(
        self,
        goals: List[int]
    ) -> Dict[str, float]:
        """
        Retorna média de gols.
        """

        average = self.calculate_average(goals)

        return {
            "average": average,
            "maximum": max(goals) if goals else 0,
            "minimum": min(goals) if goals else 0
        }
      
    # ==================================================
    # ANÁLISE OFENSIVA E DEFENSIVA
    # ==================================================

    def calculate_attack_strength(
        self,
        goals_scored: List[int],
        matches: int
    ) -> Dict[str, float]:
        """
        Calcula força ofensiva baseada em gols marcados.

        Retorna:
        - média de gols
        - índice ofensivo
        """

        if matches <= 0:
            return {
                "goals_average": 0.0,
                "attack_index": 0.0
            }

        average = sum(goals_scored) / matches

        # Índice normalizado para uso futuro
        attack_index = min(
            round(average * 50, 2),
            100
        )

        return {
            "goals_average": round(average, 2),
            "attack_index": attack_index
        }


    def calculate_defense_strength(
        self,
        goals_conceded: List[int],
        matches: int
    ) -> Dict[str, float]:
        """
        Calcula força defensiva.

        Quanto menor a média de gols sofridos,
        maior o índice defensivo.
        """

        if matches <= 0:
            return {
                "goals_conceded_average": 0.0,
                "defense_index": 0.0
            }

        average = sum(goals_conceded) / matches


        defense_index = max(
            round(
                100 - (average * 50),
                2
            ),
            0
        )

        return {
            "goals_conceded_average": round(
                average,
                2
            ),
            "defense_index": defense_index
        }


    # ==================================================
    # FORMA RECENTE DOS TIMES
    # ==================================================

    def calculate_form(
        self,
        results: List[str]
    ) -> Dict[str, Any]:
        """
        Analisa os últimos jogos.

        Entrada esperada:
        ["W", "W", "D", "L", "W"]

        W = Vitória
        D = Empate
        L = Derrota
        """

        if not results:
            return {
                "form_points": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "form_percentage": 0
            }


        wins = results.count("W")
        draws = results.count("D")
        losses = results.count("L")


        total_points = (
            wins * 3
            +
            draws
        )


        max_points = len(results) * 3


        percentage = self.calculate_percentage(
            total_points,
            max_points
        )


        return {
            "form_points": total_points,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "form_percentage": percentage
        }


    # ==================================================
    # DESEMPENHO CASA E FORA
    # ==================================================

    def home_away_analysis(
        self,
        home_goals: List[int],
        away_goals: List[int]
    ) -> Dict[str, float]:
        """
        Analisa desempenho separado.

        Útil para mercados:
        - Vitória mandante
        - Vitória visitante
        - Over/Under
        - Ambas marcam
        """

        return {

            "home_average_goals":
                self.calculate_average(
                    home_goals
                ),

            "away_average_goals":
                self.calculate_average(
                    away_goals
                ),

            "home_matches":
                len(home_goals),

            "away_matches":
                len(away_goals)
        }
          # ==================================================
    # MÉDIA MÓVEL E TENDÊNCIAS
    # ==================================================

    def moving_average(
        self,
        values: List[float],
        window: int = 5
    ) -> List[float]:
        """
        Calcula média móvel dos últimos jogos.

        Usado para identificar tendência
        de evolução ou queda de desempenho.
        """

        if not values:
            return []

        if window <= 0:
            window = 1


        averages = []

        for index in range(len(values)):

            start = max(
                0,
                index - window + 1
            )

            period = values[start:index + 1]

            averages.append(
                round(
                    sum(period) / len(period),
                    2
                )
            )


        return averages



    def performance_trend(
        self,
        values: List[float]
    ) -> Dict[str, Any]:
        """
        Identifica tendência de desempenho.

        Compara início e final da sequência.
        """

        if len(values) < 2:
            return {
                "trend": "insufficient_data",
                "variation": 0
            }


        first_average = sum(
            values[:len(values)//2]
        ) / max(
            len(values[:len(values)//2]),
            1
        )


        second_average = sum(
            values[len(values)//2:]
        ) / max(
            len(values[len(values)//2:]),
            1
        )


        variation = round(
            second_average - first_average,
            2
        )


        if variation > 0:
            trend = "improving"

        elif variation < 0:
            trend = "declining"

        else:
            trend = "stable"


        return {
            "trend": trend,
            "variation": variation
        }



    # ==================================================
    # CONSISTÊNCIA DE DESEMPENHO
    # ==================================================

    def calculate_consistency(
        self,
        values: List[float]
    ) -> Dict[str, float]:
        """
        Mede regularidade dos resultados.

        Quanto menor a variação,
        maior a consistência.
        """

        if not values:
            return {
                "standard_deviation": 0,
                "consistency_index": 0
            }


        average = (
            sum(values)
            /
            len(values)
        )


        variance = sum(
            (
                value - average
            ) ** 2

            for value in values

        ) / len(values)


        deviation = variance ** 0.5


        consistency = max(
            0,
            round(
                100 - (deviation * 20),
                2
            )
        )


        return {
            "standard_deviation":
                round(
                    deviation,
                    2
                ),

            "consistency_index":
                consistency
        }



    # ==================================================
    # VOLATILIDADE / RISCO
    # ==================================================

    def calculate_volatility(
        self,
        values: List[float]
    ) -> Dict[str, float]:
        """
        Mede instabilidade estatística.

        Importante para evitar apostas
        em mercados muito imprevisíveis.
        """

        if len(values) < 2:
            return {
                "volatility": 0,
                "risk_level": "unknown"
            }


        average = (
            sum(values)
            /
            len(values)
        )


        changes = []


        for i in range(1, len(values)):

            difference = abs(
                values[i]
                -
                values[i - 1]
            )

            changes.append(
                difference
            )


        volatility = round(
            sum(changes)
            /
            len(changes),
            2
        )


        if volatility < 1:
            risk = "low"

        elif volatility < 2:
            risk = "medium"

        else:
            risk = "high"


        return {
            "volatility": volatility,
            "risk_level": risk
      }
          # ==================================================
    # ANÁLISE DE GOLS ESPERADOS
    # ==================================================

    def expected_goals(
        self,
        goals_scored: List[int],
        goals_conceded: List[int]
    ) -> Dict[str, float]:
        """
        Estima força de criação ofensiva
        considerando gols marcados e sofridos.

        Este valor será utilizado pelos
        módulos de previsão.
        """

        if not goals_scored and not goals_conceded:
            return {
                "xg_estimate": 0,
                "attack_factor": 0,
                "defense_factor": 0
            }


        attack_factor = (
            sum(goals_scored)
            /
            max(len(goals_scored), 1)
        )


        defense_factor = (
            sum(goals_conceded)
            /
            max(len(goals_conceded), 1)
        )


        xg = (
            attack_factor
            +
            defense_factor
        ) / 2


        return {
            "xg_estimate":
                round(xg, 2),

            "attack_factor":
                round(
                    attack_factor,
                    2
                ),

            "defense_factor":
                round(
                    defense_factor,
                    2
                )
        }



    # ==================================================
    # PROBABILIDADE OVER / UNDER
    # ==================================================

    def over_under_probability(
        self,
        goals_history: List[int],
        line: float = 2.5
    ) -> Dict[str, float]:
        """
        Calcula frequência histórica
        acima ou abaixo de uma linha de gols.

        Exemplo:
        Over 2.5
        Under 2.5
        """

        if not goals_history:
            return {
                "over_probability": 0,
                "under_probability": 0
            }


        over_count = sum(
            1
            for goals in goals_history
            if goals > line
        )


        under_count = sum(
            1
            for goals in goals_history
            if goals <= line
        )


        total = len(goals_history)


        return {

            "over_probability":
                round(
                    (
                        over_count
                        /
                        total
                    )
                    *
                    100,
                    2
                ),


            "under_probability":
                round(
                    (
                        under_count
                        /
                        total
                    )
                    *
                    100,
                    2
                )
        }



    # ==================================================
    # AMBAS MARCAM (BTTS)
    # ==================================================

    def btts_probability(
        self,
        scored_team_a: List[int],
        scored_team_b: List[int]
    ) -> Dict[str, float]:
        """
        Calcula probabilidade estatística
        de ambas as equipes marcarem.
        """

        if not scored_team_a or not scored_team_b:
            return {
                "btts_yes": 0,
                "btts_no": 0
            }


        matches = min(
            len(scored_team_a),
            len(scored_team_b)
        )


        yes = 0


        for i in range(matches):

            if (
                scored_team_a[i] > 0
                and
                scored_team_b[i] > 0
            ):
                yes += 1


        probability = round(
            (
                yes
                /
                matches
            )
            *
            100,
            2
        )


        return {

            "btts_yes":
                probability,

            "btts_no":
                round(
                    100 - probability,
                    2
                )
        }



    # ==================================================
    # DISTRIBUIÇÃO DE GOLS
    # ==================================================

    def goal_distribution(
        self,
        goals: List[int]
    ) -> Dict[str, float]:
        """
        Distribui frequência de gols.

        Ajuda a identificar padrões:
        0 gols, 1 gol, 2 gols, 3+ gols.
        """

        if not goals:
            return {}


        total = len(goals)


        distribution = {

            "0_goals": 0,
            "1_goal": 0,
            "2_goals": 0,
            "3_plus_goals": 0

        }


        for value in goals:

            if value == 0:
                distribution["0_goals"] += 1

            elif value == 1:
                distribution["1_goal"] += 1

            elif value == 2:
                distribution["2_goals"] += 1

            else:
                distribution["3_plus_goals"] += 1



        for key in distribution:

            distribution[key] = round(
                (
                    distribution[key]
                    /
                    total
                )
                *
                100,
                2
            )


        return distribution
          # ==================================================
    # RANKING DE FORÇA DAS EQUIPES
    # ==================================================

    def team_strength_rating(
        self,
        attack_index: float,
        defense_index: float,
        form_percentage: float,
        consistency_index: float
    ) -> Dict[str, float]:
        """
        Cria um índice geral de força da equipe.

        Combina:
        - ataque
        - defesa
        - momento atual
        - regularidade

        Resultado utilizado pelos módulos
        de análise e previsão.
        """

        rating = (
            (attack_index * 0.30)
            +
            (defense_index * 0.30)
            +
            (form_percentage * 0.25)
            +
            (consistency_index * 0.15)
        )


        return {

            "strength_rating":
                round(
                    min(rating, 100),
                    2
                )
        }



    # ==================================================
    # COMPARAÇÃO ENTRE EQUIPES
    # ==================================================

    def compare_teams(
        self,
        team_a: Dict[str, float],
        team_b: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compara dois times estatisticamente.

        Retorna vantagem relativa.
        """

        keys = [
            "attack",
            "defense",
            "form",
            "strength"
        ]


        comparison = {}


        advantage_a = 0
        advantage_b = 0


        for key in keys:

            value_a = team_a.get(
                key,
                0
            )

            value_b = team_b.get(
                key,
                0
            )


            difference = round(
                value_a - value_b,
                2
            )


            comparison[key] = {
                "team_a": value_a,
                "team_b": value_b,
                "difference": difference
            }


            if difference > 0:
                advantage_a += 1

            elif difference < 0:
                advantage_b += 1



        if advantage_a > advantage_b:
            winner = "team_a"

        elif advantage_b > advantage_a:
            winner = "team_b"

        else:
            winner = "balanced"



        comparison["overall_advantage"] = winner


        return comparison



    # ==================================================
    # VANTAGEM DE MANDO
    # ==================================================

    def home_advantage(
        self,
        home_wins: int,
        home_matches: int
    ) -> Dict[str, float]:
        """
        Calcula impacto do mando de campo.
        """

        if home_matches == 0:
            return {
                "home_advantage": 0
            }


        percentage = (
            home_wins
            /
            home_matches
        ) * 100


        return {

            "home_advantage":
                round(
                    percentage,
                    2
                )
        }



    # ==================================================
    # ÍNDICE GERAL DE CONFIANÇA
    # ==================================================

    def confidence_score(
        self,
        sample_size: int,
        consistency: float,
        volatility: float
    ) -> Dict[str, Any]:
        """
        Calcula confiança estatística
        dos dados analisados.

        Quanto maior a amostra e consistência,
        maior a confiabilidade.
        """

        sample_factor = min(
            sample_size * 10,
            100
        )


        volatility_factor = max(
            100 - (volatility * 20),
            0
        )


        confidence = (
            sample_factor * 0.40
            +
            consistency * 0.40
            +
            volatility_factor * 0.20
        )


        confidence = min(
            round(confidence, 2),
            100
        )


        if confidence >= 75:
            level = "high"

        elif confidence >= 50:
            level = "medium"

        else:
            level = "low"



        return {

            "confidence_score":
                confidence,

            "confidence_level":
                level
        }



    # ==================================================
    # RESUMO ESTATÍSTICO COMPLETO
    # ==================================================

    def generate_summary(
        self,
        team_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza todas as métricas
        em uma estrutura única.

        Será consumido pelo sistema
        de análise do OddReal.
        """

        return {

            "team":
                team_data.get(
                    "team",
                    "unknown"
                ),

            "attack":
                team_data.get(
                    "attack",
                    {}
                ),

            "defense":
                team_data.get(
                    "defense",
                    {}
                ),

            "form":
                team_data.get(
                    "form",
                    {}
                ),

            "strength":
                team_data.get(
                    "strength",
                    {}
                ),

            "generated_at":
                datetime.now().isoformat()
      }
          # ==================================================
    # NORMALIZAÇÃO DE DADOS DA API
    # ==================================================

    def normalize_team_statistics(
        self,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Padroniza dados recebidos da API.

        Diferentes fontes podem retornar
        estruturas diferentes. Este método
        cria um formato único para o OddReal.
        """

        if not raw_data:

            return {
                "team": "unknown",
                "goals_scored": [],
                "goals_conceded": [],
                "results": []
            }


        return {

            "team":
                raw_data.get(
                    "team",
                    "unknown"
                ),

            "goals_scored":
                raw_data.get(
                    "goals_scored",
                    []
                ),

            "goals_conceded":
                raw_data.get(
                    "goals_conceded",
                    []
                ),

            "results":
                raw_data.get(
                    "results",
                    []
                ),

            "matches":
                raw_data.get(
                    "matches",
                    0
                )
        }



    # ==================================================
    # PROCESSAMENTO COMPLETO DE EQUIPE
    # ==================================================

    def process_team(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa todas as análises estatísticas
        de uma equipe em uma única chamada.
        """

        normalized = self.normalize_team_statistics(
            data
        )


        goals_scored = normalized[
            "goals_scored"
        ]

        goals_conceded = normalized[
            "goals_conceded"
        ]


        matches = max(
            normalized.get(
                "matches",
                len(goals_scored)
            ),
            1
        )


        attack = self.calculate_attack_strength(
            goals_scored,
            matches
        )


        defense = self.calculate_defense_strength(
            goals_conceded,
            matches
        )


        form = self.calculate_form(
            normalized["results"]
        )


        consistency = self.calculate_consistency(
            goals_scored
        )


        volatility = self.calculate_volatility(
            goals_scored
        )


        strength = self.team_strength_rating(
            attack["attack_index"],
            defense["defense_index"],
            form["form_percentage"],
            consistency["consistency_index"]
        )


        confidence = self.confidence_score(
            matches,
            consistency["consistency_index"],
            volatility["volatility"]
        )


        return {

            "team":
                normalized["team"],

            "attack":
                attack,

            "defense":
                defense,

            "form":
                form,

            "consistency":
                consistency,

            "volatility":
                volatility,

            "strength":
                strength,

            "confidence":
                confidence
        }



    # ==================================================
    # COMPARAÇÃO COMPLETA DE PARTIDA
    # ==================================================

    def analyze_match(
        self,
        home_team: Dict[str, Any],
        away_team: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa confronto completo.
        """

        home_analysis = self.process_team(
            home_team
        )


        away_analysis = self.process_team(
            away_team
        )


        comparison = self.compare_teams(

            {
                "attack":
                    home_analysis["attack"]["attack_index"],

                "defense":
                    home_analysis["defense"]["defense_index"],

                "form":
                    home_analysis["form"]["form_percentage"],

                "strength":
                    home_analysis["strength"]["strength_rating"]
            },

            {
                "attack":
                    away_analysis["attack"]["attack_index"],

                "defense":
                    away_analysis["defense"]["defense_index"],

                "form":
                    away_analysis["form"]["form_percentage"],

                "strength":
                    away_analysis["strength"]["strength_rating"]
            }
        )


        return {

            "home":
                home_analysis,

            "away":
                away_analysis,

            "comparison":
                comparison,

            "generated_at":
                datetime.now().isoformat()
        }



# ======================================================
# INSTÂNCIA GLOBAL DO MOTOR
# ======================================================

statistics_engine = StatisticsEngine()
