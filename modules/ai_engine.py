"""
OddReal 2.0
Motor de Inteligência Artificial

Responsável por:

- Receber análises estruturadas;
- Preparar contexto para IA;
- Gerar diagnóstico técnico;
- Identificar pontos fortes e fracos;
- Produzir explicações em linguagem simples;
- Gerar alertas;
- Evitar que a IA altere os cálculos matemáticos do OddsEngine.

A IA é uma camada interpretativa.
Os cálculos quantitativos continuam sendo responsabilidade
do OddsEngine.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class AIEngine:
    """
    Motor de IA do OddReal.

    O mecanismo foi estruturado para permitir posteriormente
    conexão com OpenAI, outro provedor LLM ou modelo local,
    sem alterar o restante da aplicação.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:

        self.provider = (
            provider
            or "local"
        )

        self.model = (
            model
            or "default"
        )

        self.enabled = True

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    def enable(self) -> None:
        """
        Ativa o mecanismo de IA.
        """

        self.enabled = True

    def disable(self) -> None:
        """
        Desativa o mecanismo de IA.
        """

        self.enabled = False

    # ==========================================================
    # PREPARAÇÃO DOS DADOS
    # ==========================================================

    def prepare_context(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extrai somente os dados relevantes para a IA.
        """

        if not isinstance(
            analysis,
            dict,
        ):

            return {}

        return {

            "event_id": analysis.get(
                "id"
            ),

            "sport": analysis.get(
                "sport_title",
                analysis.get(
                    "sport_key"
                ),
            ),

            "home_team": analysis.get(
                "home_team"
            ),

            "away_team": analysis.get(
                "away_team"
            ),

            "market": analysis.get(
                "selected_market"
            ),

            "outcome": analysis.get(
                "selected_outcome"
            ),

            "bookmaker": analysis.get(
                "selected_bookmaker"
            ),

            "odd": analysis.get(
                "odd"
            ),

            "probability": analysis.get(
                "probability"
            ),

            "expected_value": analysis.get(
                "expected_value"
            ),

            "oddreal_index": analysis.get(
                "oddreal_index"
            ),

            "confidence_level": analysis.get(
                "confidence_level"
            ),

            "average_odd": analysis.get(
                "average_odd"
            ),

            "market_variation": analysis.get(
                "market_variation"
            ),

            "risk": analysis.get(
                "risk"
            ),

            "is_value_bet": analysis.get(
                "is_value_bet",
                False,
            ),

        }

    # ==========================================================
    # PROMPT
    # ==========================================================

    def build_prompt(
        self,
        analysis: Dict[str, Any],
    ) -> str:
        """
        Constrói o contexto textual que será enviado ao
        modelo de IA quando um provedor real estiver conectado.
        """

        context = self.prepare_context(
            analysis
        )

        return f"""
Você é o módulo de inteligência analítica do OddReal 2.0.

Analise tecnicamente os dados abaixo.

IMPORTANTE:
- Não invente estatísticas.
- Não invente lesões.
- Não invente escalações.
- Não invente notícias.
- Não altere os cálculos fornecidos.
- Diferencie fatos de inferências.
- Uma Value Bet não significa aposta garantida.
- Probabilidade, EV e Índice OddReal são indicadores
  matemáticos e devem ser tratados como estimativas.

DADOS:

{json.dumps(
    context,
    ensure_ascii=False,
    indent=2,
)}

Produza uma análise contendo:

1. Resumo do evento.
2. Interpretação da odd.
3. Interpretação da probabilidade.
4. Interpretação do EV.
5. Interpretação do Índice OddReal.
6. Relação entre a melhor odd e a média do mercado.
7. Avaliação do nível de risco.
8. Pontos favoráveis.
9. Pontos de atenção.
10. Conclusão técnica.

Não trate a análise como garantia de resultado.
"""

    # ==========================================================
    # ANÁLISE LOCAL
    # ==========================================================

    def local_analysis(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Gera uma interpretação local baseada somente nos
        indicadores já calculados.

        Esta função não substitui um LLM.
        Ela permite que o sistema continue funcional
        mesmo sem API de IA configurada.
        """

        context = self.prepare_context(
            analysis
        )

        if not context:

            return {

                "status": "error",

                "message": (
                    "Dados insuficientes "
                    "para análise."
                ),

            }

        probability = float(
            context.get(
                "probability",
                0,
            )
            or 0
        )

        ev = float(
            context.get(
                "expected_value",
                0,
            )
            or 0
        )

        index = int(
            context.get(
                "oddreal_index",
                0,
            )
            or 0
        )

        variation = float(
            context.get(
                "market_variation",
                0,
            )
            or 0
        )

        risk = context.get(
            "risk",
            "Alto",
        )

        is_value = bool(
            context.get(
                "is_value_bet",
                False,
            )
        )

        strengths: List[str] = []

        warnings: List[str] = []

        # ------------------------------------------------------
        # PROBABILIDADE
        # ------------------------------------------------------

        if probability >= 70:

            strengths.append(
                "Probabilidade estimada elevada."
            )

        elif probability >= 55:

            strengths.append(
                "Probabilidade estimada em "
                "faixa intermediária."
            )

        else:

            warnings.append(
                "Probabilidade estimada "
                "relativamente baixa."
            )

        # ------------------------------------------------------
        # EV
        # ------------------------------------------------------

        if ev >= 10:

            strengths.append(
                "Valor esperado fortemente positivo."
            )

        elif ev >= 5:

            strengths.append(
                "Valor esperado positivo "
                "e relevante."
            )

        elif ev > 0:

            strengths.append(
                "Valor esperado positivo, "
                "porém limitado."
            )

        else:

            warnings.append(
                "Valor esperado não indica "
                "vantagem matemática positiva."
            )

        # ------------------------------------------------------
        # ÍNDICE
        # ------------------------------------------------------

        if index >= 85:

            strengths.append(
                "Índice OddReal classificado "
                "como muito alto."
            )

        elif index >= 70:

            strengths.append(
                "Índice OddReal classificado "
                "como alto."
            )

        elif index >= 55:

            strengths.append(
                "Índice OddReal classificado "
                "como médio."
            )

        else:

            warnings.append(
                "Índice OddReal abaixo da "
                "faixa considerada forte."
            )

        # ------------------------------------------------------
        # MERCADO
        # ------------------------------------------------------

        if variation > 5:

            strengths.append(
                "A melhor odd está "
                "consideravelmente acima "
                "da média encontrada."
            )

        elif variation < -5:

            warnings.append(
                "A odd analisada está abaixo "
                "da média encontrada no mercado."
            )

        else:

            strengths.append(
                "A odd está relativamente "
                "próxima do consenso de mercado."
            )

        # ------------------------------------------------------
        # VALUE BET
        # ------------------------------------------------------

        if is_value:

            strengths.append(
                "A oportunidade ultrapassa "
                "o limite padrão de Value Bet."
            )

        else:

            warnings.append(
                "A oportunidade não ultrapassa "
                "o limite padrão de Value Bet."
            )

        # ------------------------------------------------------
        # CONCLUSÃO
        # ------------------------------------------------------

        if (
            is_value
            and index >= 70
            and ev >= 10
        ):

            conclusion = (
                "Os indicadores apresentam "
                "um cenário matematicamente "
                "favorável segundo os critérios "
                "do OddReal."
            )

        elif ev > 0:

            conclusion = (
                "Existe sinal matemático positivo, "
                "mas os indicadores não são "
                "suficientes para classificar "
                "o cenário como excepcional."
            )

        else:

            conclusion = (
                "Os indicadores disponíveis "
                "não apresentam vantagem "
                "matemática suficientemente clara."
            )

        return {

            "status": "success",

            "provider": self.provider,

            "model": self.model,

            "event": {

                "home_team": context.get(
                    "home_team"
                ),

                "away_team": context.get(
                    "away_team"
                ),

                "sport": context.get(
                    "sport"
                ),

                "market": context.get(
                    "market"
                ),

                "outcome": context.get(
                    "outcome"
                ),

            },

            "indicators": {

                "odd": context.get(
                    "odd"
                ),

                "probability": probability,

                "expected_value": ev,

                "oddreal_index": index,

                "confidence_level": context.get(
                    "confidence_level"
                ),

                "average_odd": context.get(
                    "average_odd"
                ),

                "market_variation": variation,

                "risk": risk,

                "is_value_bet": is_value,

            },

            "strengths": strengths,

            "warnings": warnings,

            "conclusion": conclusion,

        }

    # ==========================================================
    # ANÁLISE
    # ==========================================================

    def analyze(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa análise de IA.

        Por enquanto utiliza o mecanismo local.
        O ponto de entrada foi criado para permitir conexão
        futura com um LLM sem alterar o restante do sistema.
        """

        if not self.enabled:

            return {

                "status": "disabled",

                "message": (
                    "Motor de IA desativado."
                ),

            }

        return self.local_analysis(
            analysis
        )

    # ==========================================================
    # ANÁLISE EM LOTE
    # ==========================================================

    def analyze_many(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Executa análise sobre vários eventos.
        """

        if not isinstance(
            analyses,
            list,
        ):

            return []

        results: List[
            Dict[str, Any]
        ] = []

        for analysis in analyses:

            result = self.analyze(
                analysis
            )

            if result:

                results.append(
                    result
                )

        return results


ai_engine = AIEngine()
