"""
OddReal 2.0
Módulo: analysis.py

Responsável pela interpretação dos dados estatísticos.

Funções:
- Análise de confronto
- Identificação de vantagens
- Leitura de tendências
- Avaliação de mercados
- Geração de insights

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime


class MatchAnalyzer:
    """
    Motor de análise inteligente do OddReal.

    Recebe dados estatísticos e transforma
    em informações estratégicas.
    """


    def __init__(self):

        self.version = "2.0"
        self.created_at = datetime.now()



    # ==================================================
    # VALIDAÇÃO DE ENTRADA
    # ==================================================

    @staticmethod
    def validate_match_data(
        data: Dict[str, Any]
    ) -> bool:
        """
        Verifica se existe informação
        suficiente para análise.
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
    # EXTRAÇÃO DE FORÇA DOS TIMES
    # ==================================================

    def extract_strength(
        self,
        team_data: Dict[str, Any]
    ) -> float:
        """
        Obtém índice de força da equipe.
        """

        return (
            team_data
            .get(
                "strength",
                {}
            )
            .get(
                "strength_rating",
                0
            )
        )



    # ==================================================
    # COMPARAÇÃO DE PODERIO
    # ==================================================

    def compare_strength(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara força geral dos times.
        """

        home_strength = self.extract_strength(
            home
        )


        away_strength = self.extract_strength(
            away
        )


        difference = round(
            home_strength
            -
            away_strength,
            2
        )


        if difference > 10:

            advantage = "home"

        elif difference < -10:

            advantage = "away"

        else:

            advantage = "balanced"



        return {

            "home_strength":
                home_strength,

            "away_strength":
                away_strength,

            "difference":
                difference,

            "advantage":
                advantage
        }
          # ==================================================
    # ANÁLISE OFENSIVA VS DEFENSIVA
    # ==================================================

    def analyze_attack_defense(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara capacidade ofensiva
        contra resistência defensiva.
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


        home_attack_vs_defense = round(
            home_attack
            -
            (100 - away_defense),
            2
        )


        away_attack_vs_defense = round(
            away_attack
            -
            (100 - home_defense),
            2
        )


        return {

            "home_attack_power":
                home_attack,

            "away_attack_power":
                away_attack,

            "home_defensive_strength":
                home_defense,

            "away_defensive_strength":
                away_defense,

            "home_attack_matchup":
                home_attack_vs_defense,

            "away_attack_matchup":
                away_attack_vs_defense
        }



    # ==================================================
    # IDENTIFICAÇÃO DE PONTOS FORTES E FRACOS
    # ==================================================

    def identify_team_profile(
        self,
        team: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Cria perfil técnico da equipe.
        """

        strengths = []
        weaknesses = []


        attack = (
            team
            .get(
                "attack",
                {}
            )
            .get(
                "attack_index",
                0
            )
        )


        defense = (
            team
            .get(
                "defense",
                {}
            )
            .get(
                "defense_index",
                0
            )
        )


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


        consistency = (
            team
            .get(
                "consistency",
                {}
            )
            .get(
                "consistency_index",
                0
            )
        )


        if attack >= 70:
            strengths.append(
                "strong_attack"
            )

        elif attack < 40:
            weaknesses.append(
                "weak_attack"
            )



        if defense >= 70:
            strengths.append(
                "strong_defense"
            )

        elif defense < 40:
            weaknesses.append(
                "weak_defense"
            )



        if form >= 70:
            strengths.append(
                "good_recent_form"
            )

        elif form < 40:
            weaknesses.append(
                "poor_recent_form"
            )



        if consistency >= 70:
            strengths.append(
                "consistent_team"
            )

        elif consistency < 40:
            weaknesses.append(
                "unstable_team"
            )


        return {

            "strengths":
                strengths,

            "weaknesses":
                weaknesses
        }



    # ==================================================
    # CLASSIFICAÇÃO DO CONFRONTO
    # ==================================================

    def classify_match(
        self,
        comparison: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Define o perfil geral da partida.
        """

        difference = abs(
            comparison
            .get(
                "difference",
                0
            )
        )


        if difference >= 25:

            category = "mismatch"

            description = (
                "Grande diferença técnica "
                "entre as equipes"
            )


        elif difference >= 10:

            category = "advantage"

            description = (
                "Uma equipe apresenta "
                "vantagem estatística"
            )


        else:

            category = "balanced"

            description = (
                "Confronto equilibrado "
                "estatisticamente"
            )


        return {

            "category":
                category,

            "description":
                description
          }
          # ==================================================
    # ANÁLISE DE MERCADO OVER / UNDER
    # ==================================================

    def analyze_over_under(
        self,
        statistics: Dict[str, Any],
        line: float = 2.5
    ) -> Dict[str, Any]:
        """
        Analisa tendência de gols
        para mercados Over/Under.
        """

        over_probability = (
            statistics
            .get(
                "over_probability",
                0
            )
        )


        under_probability = (
            statistics
            .get(
                "under_probability",
                0
            )
        )


        if over_probability >= 65:

            recommendation = "over"

            confidence = over_probability


        elif under_probability >= 65:

            recommendation = "under"

            confidence = under_probability


        else:

            recommendation = "uncertain"

            confidence = max(
                over_probability,
                under_probability
            )


        return {

            "market":
                f"over_under_{line}",

            "recommendation":
                recommendation,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "over_probability":
                over_probability,

            "under_probability":
                under_probability
        }



    # ==================================================
    # ANÁLISE AMBAS MARCAM
    # ==================================================

    def analyze_btts(
        self,
        btts_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Avalia mercado Ambas Marcam.
        """

        yes_probability = (
            btts_data
            .get(
                "btts_yes",
                0
            )
        )


        no_probability = (
            btts_data
            .get(
                "btts_no",
                0
            )
        )


        if yes_probability >= 65:

            signal = "btts_yes"

            confidence = yes_probability


        elif no_probability >= 65:

            signal = "btts_no"

            confidence = no_probability


        else:

            signal = "balanced"

            confidence = max(
                yes_probability,
                no_probability
            )


        return {

            "market":
                "both_teams_score",

            "signal":
                signal,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "yes_probability":
                yes_probability,

            "no_probability":
                no_probability
        }



    # ==================================================
    # ÍNDICE DE POTENCIAL DE GOLS
    # ==================================================

    def goal_potential_index(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula potencial ofensivo
        da partida.
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


        attack_score = (
            home_attack
            +
            away_attack
        ) / 2


        defensive_factor = (
            (100 - home_defense)
            +
            (100 - away_defense)
        ) / 2


        goal_index = round(
            (
                attack_score * 0.6
                +
                defensive_factor * 0.4
            ),
            2
        )


        if goal_index >= 70:

            classification = "high_goal_potential"

        elif goal_index >= 45:

            classification = "medium_goal_potential"

        else:

            classification = "low_goal_potential"


        return {

            "goal_index":
                goal_index,

            "classification":
                classification
        }



    # ==================================================
    # ANÁLISE DE RISCO DA PARTIDA
    # ==================================================

    def match_risk_analysis(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Avalia o nível de imprevisibilidade.
        """

        home_volatility = (
            home
            .get(
                "volatility",
                {}
            )
            .get(
                "volatility",
                0
            )
        )


        away_volatility = (
            away
            .get(
                "volatility",
                {}
            )
            .get(
                "volatility",
                0
            )
        )


        average_risk = round(
            (
                home_volatility
                +
                away_volatility
            )
            /
            2,
            2
        )


        if average_risk < 1:

            level = "low"

        elif average_risk < 2:

            level = "medium"

        else:

            level = "high"



        return {

            "risk_score":
                average_risk,

            "risk_level":
                level
      }
          # ==================================================
    # GERAÇÃO DE INSIGHTS AUTOMÁTICOS
    # ==================================================

    def generate_insights(
        self,
        analysis_data: Dict[str, Any]
    ) -> List[str]:
        """
        Cria observações automáticas
        baseadas nos indicadores.
        """

        insights = []


        comparison = analysis_data.get(
            "comparison",
            {}
        )


        advantage = comparison.get(
            "advantage",
            "balanced"
        )


        if advantage == "home":

            insights.append(
                "Mandante apresenta vantagem estatística."
            )

        elif advantage == "away":

            insights.append(
                "Visitante apresenta vantagem estatística."
            )

        else:

            insights.append(
                "Confronto equilibrado tecnicamente."
            )



        goal_data = analysis_data.get(
            "goal_potential",
            {}
        )


        goal_classification = (
            goal_data
            .get(
                "classification",
                ""
            )
        )


        if goal_classification == "high_goal_potential":

            insights.append(
                "Partida possui tendência ofensiva elevada."
            )

        elif goal_classification == "low_goal_potential":

            insights.append(
                "Dados indicam possível jogo de poucos gols."
            )



        risk = analysis_data.get(
            "risk",
            {}
        )


        if risk.get(
            "risk_level"
        ) == "high":

            insights.append(
                "Atenção: confronto apresenta alta volatilidade."
            )


        return insights



    # ==================================================
    # DETECÇÃO DE OPORTUNIDADE ESTATÍSTICA
    # ==================================================

    def detect_value_opportunity(
        self,
        markets: Dict[str, Any],
        minimum_confidence: float = 65
    ) -> List[Dict[str, Any]]:
        """
        Identifica mercados com maior
        suporte estatístico.
        """

        opportunities = []


        for market_name, data in markets.items():

            confidence = data.get(
                "confidence",
                0
            )


            if confidence >= minimum_confidence:

                opportunities.append(

                    {

                        "market":
                            market_name,

                        "confidence":
                            confidence,

                        "status":
                            "possible_value"

                    }

                )


        return opportunities



    # ==================================================
    # SCORE GERAL DA PARTIDA
    # ==================================================

    def calculate_match_score(
        self,
        home: Dict[str, Any],
        away: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Cria uma nota geral do confronto.

        Utiliza:
        - força
        - forma
        - consistência
        """

        home_strength = (
            home
            .get(
                "strength",
                {}
            )
            .get(
                "strength_rating",
                0
            )
        )


        away_strength = (
            away
            .get(
                "strength",
                {}
            )
            .get(
                "strength_rating",
                0
            )
        )


        home_confidence = (
            home
            .get(
                "confidence",
                {}
            )
            .get(
                "confidence_score",
                0
            )
        )


        away_confidence = (
            away
            .get(
                "confidence",
                {}
            )
            .get(
                "confidence_score",
                0
            )
        )


        home_score = round(
            (
                home_strength * 0.7
                +
                home_confidence * 0.3
            ),
            2
        )


        away_score = round(
            (
                away_strength * 0.7
                +
                away_confidence * 0.3
            ),
            2
        )


        return {

            "home_score":
                home_score,

            "away_score":
                away_score,

            "difference":
                round(
                    home_score
                    -
                    away_score,
                    2
                )
        }



    # ==================================================
    # RESUMO EXECUTIVO
    # ==================================================

    def create_summary(
        self,
        match_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria resumo final para apresentação.
        """

        return {

            "classification":
                match_analysis
                .get(
                    "classification",
                    {}
                ),

            "insights":
                match_analysis
                .get(
                    "insights",
                    []
                ),

            "opportunities":
                match_analysis
                .get(
                    "opportunities",
                    []
                ),

            "generated_at":
                datetime.now().isoformat()

        }
          # ==================================================
    # PIPELINE COMPLETO DE ANÁLISE
    # ==================================================

    def run_analysis(
        self,
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa todas as etapas de análise
        de uma partida.

        Fluxo:

        Dados estatísticos
              ↓
        Comparação técnica
              ↓
        Mercados
              ↓
        Riscos
              ↓
        Insights
              ↓
        Relatório final
        """

        if not self.validate_match_data(
            match_data
        ):

            return {

                "status":
                    "error",

                "message":
                    "Dados insuficientes para análise"

            }



        home = match_data["home"]

        away = match_data["away"]



        # Comparação de força

        comparison = self.compare_strength(
            home,
            away
        )



        # Análise ofensiva/defensiva

        attack_defense = (
            self.analyze_attack_defense(
                home,
                away
            )
        )



        # Perfis das equipes

        home_profile = (
            self.identify_team_profile(
                home
            )
        )


        away_profile = (
            self.identify_team_profile(
                away
            )
        )



        # Classificação do jogo

        classification = (
            self.classify_match(
                comparison
            )
        )



        # Potencial de gols

        goal_potential = (
            self.goal_potential_index(
                home,
                away
            )
        )



        # Risco

        risk = (
            self.match_risk_analysis(
                home,
                away
            )
        )



        # Score geral

        match_score = (
            self.calculate_match_score(
                home,
                away
            )
        )



        result = {

            "comparison":
                comparison,

            "attack_defense":
                attack_defense,

            "home_profile":
                home_profile,

            "away_profile":
                away_profile,

            "classification":
                classification,

            "goal_potential":
                goal_potential,

            "risk":
                risk,

            "match_score":
                match_score

        }



        # Insights

        result["insights"] = (
            self.generate_insights(
                result
            )
        )



        return {

            "status":
                "success",

            "analysis":
                result,

            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # ANÁLISE DE MÚLTIPLAS PARTIDAS
    # ==================================================

    def analyze_multiple_matches(
        self,
        matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processa uma lista de jogos.
        """

        results = []


        for match in matches:

            analysis = (
                self.run_analysis(
                    match
                )
            )


            results.append(
                analysis
            )


        return results



    # ==================================================
    # FILTRO DE MELHORES OPORTUNIDADES
    # ==================================================

    def rank_opportunities(
        self,
        analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ordena partidas pelo potencial
        estatístico encontrado.
        """

        ranked = []


        for item in analyses:

            if (
                item.get("status")
                !=
                "success"
            ):

                continue


            analysis = item.get(
                "analysis",
                {}
            )


            score = (
                analysis
                .get(
                    "match_score",
                    {}
                )
                .get(
                    "difference",
                    0
                )
            )


            ranked.append(

                {

                    "analysis":
                        analysis,

                    "priority_score":
                        abs(score)

                }

            )



        ranked.sort(
            key=lambda x:
            x["priority_score"],
            reverse=True
        )


        return ranked
          # ==================================================
    # EXPORTAÇÃO DE RELATÓRIO
    # ==================================================

    def export_report(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza a análise em formato
        pronto para exibição no sistema.
        """

        if not analysis:

            return {

                "status":
                    "empty",

                "report":
                    {}

            }



        report = {

            "match_classification":
                analysis
                .get(
                    "classification",
                    {}
                ),


            "technical_comparison":
                analysis
                .get(
                    "comparison",
                    {}
                ),


            "goal_analysis":
                analysis
                .get(
                    "goal_potential",
                    {}
                ),


            "risk_analysis":
                analysis
                .get(
                    "risk",
                    {}
                ),


            "insights":
                analysis
                .get(
                    "insights",
                    []
                ),


            "match_score":
                analysis
                .get(
                    "match_score",
                    {}
                )

        }


        return {

            "status":
                "success",

            "report":
                report,

            "generated_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # FORMATAÇÃO DE TEXTO ANALÍTICO
    # ==================================================

    def generate_text_summary(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """
        Converte dados técnicos em
        resumo textual para o usuário.
        """

        if not analysis:

            return (
                "Não foi possível gerar análise."
            )


        classification = (
            analysis
            .get(
                "classification",
                {}
            )
            .get(
                "category",
                "unknown"
            )
        )


        insights = analysis.get(
            "insights",
            []
        )


        text = (
            f"Classificação do confronto: "
            f"{classification}.\n\n"
        )


        if insights:

            text += (
                "Principais pontos:\n"
            )


            for item in insights:

                text += (
                    f"- {item}\n"
                )


        return text



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
                "analysis",

            "version":
                self.version,

            "initialized":
                True,

            "created_at":
                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO ANALISADOR
# ======================================================

match_analyzer = MatchAnalyzer()
