"""
OddReal 2.0
Pipeline Principal

Fluxo:

The Odds API
    ↓
API Client
    ↓
DataManager
    ↓
Normalização / preparação
    ↓
Analyzer
    ↓
EV
    ↓
Value Bets
    ↓
Melhores oportunidades
    ↓
IA
    ↓
Dashboard

Responsabilidade deste módulo:
- Orquestrar o fluxo completo;
- Não realizar cálculos quantitativos próprios;
- Preservar os dados recebidos;
- Entregar os dados ao Analyzer;
- Consolidar EV e Value Bets;
- Preparar dados para IA;
- Entregar um resultado único para a interface.

IMPORTANTE:

O Pipeline NÃO implementa a lógica matemática das odds.

A responsabilidade quantitativa pertence ao Analyzer.

O Pipeline apenas coordena os módulos.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from services.api_client import api_client
from modules.data_manager import data_manager
from modules.logger import info, error
from core.analyzer import analyzer


class Pipeline:
    """
    Orquestrador principal do OddReal 2.0.

    Fluxo:

        API
         ↓
        DataManager
         ↓
        Analyzer
         ↓
        Value Bets
         ↓
        IA
         ↓
        Dashboard

    O Pipeline não recalcula EV, probabilidade,
    margem, índice ou qualquer métrica quantitativa.
    """

    def __init__(self) -> None:
        info(
            "Pipeline OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _safe_list(
        value: Any,
    ) -> List[Any]:
        """
        Garante que o valor retornado seja uma lista.
        """

        if isinstance(value, list):
            return value

        return []

    @staticmethod
    def _safe_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Garante que o valor retornado seja um dicionário.
        """

        if isinstance(value, dict):
            return value

        return {}

    # ==========================================================
    # PREPARAÇÃO DOS EVENTOS
    # ==========================================================

    def _prepare_events(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Preserva os eventos recebidos.

        O Analyzer é responsável por interpretar:

        - bookmakers;
        - mercados;
        - outcomes;
        - odds;
        - probabilidades;
        - EV;
        - Value Bets.

        Portanto, o Pipeline não reconstrói
        nem modifica a estrutura quantitativa.
        """

        if not isinstance(events, list):
            return []

        prepared_events: List[
            Dict[str, Any]
        ] = []

        for event in events:

            if not isinstance(event, dict):
                continue

            prepared_events.append(
                deepcopy(event)
            )

        return prepared_events

    # ==========================================================
    # EXECUÇÃO PRINCIPAL
    # ==========================================================

    def execute(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Executa o pipeline completo do OddReal.

        Fluxo:

        1. Coleta da API
        2. DataManager
        3. Analyzer
        4. Value Bets
        5. Melhores oportunidades
        6. Melhor oportunidade
        7. Dados para IA
        8. Consolidação
        """

        # ======================================================
        # 1. COLETA DA API
        # ======================================================

        try:

            raw_events = api_client.get_events(
                force_refresh=force_refresh
            )

            raw_events = self._safe_list(
                raw_events
            )

        except Exception as exc:

            error(
                "Erro na coleta da API: "
                f"{exc}"
            )

            raw_events = []

        # ======================================================
        # 2. DATA MANAGER
        # ======================================================

        try:

            managed_data = data_manager.process(
                raw_events
            )

            managed_data = self._safe_dict(
                managed_data
            )

        except Exception as exc:

            error(
                "Erro no DataManager: "
                f"{exc}"
            )

            managed_data = {
                "raw_events": deepcopy(
                    raw_events
                ),
                "clean_events": [],
                "analysis_events": [],
                "analysis_records": [],
                "summary": {},
            }

        # ======================================================
        # 3. DADOS DO DATAMANAGER
        # ======================================================

        analysis_events = self._safe_list(
            managed_data.get(
                "analysis_events",
                [],
            )
        )

        analysis_records = self._safe_list(
            managed_data.get(
                "analysis_records",
                [],
            )
        )

        clean_events = self._safe_list(
            managed_data.get(
                "clean_events",
                [],
            )
        )

        # ======================================================
        # 4. ANALYZER
        # ======================================================

        try:

            analyzer_result = analyzer.process(
                managed_data
            )

            analyzer_result = self._safe_dict(
                analyzer_result
            )

        except Exception as exc:

            error(
                "Erro no Analyzer: "
                f"{exc}"
            )

            analyzer_result = {
                "analyses": [],
                "value_bets": [],
                "summary": {},
                "processed_at": None,
                "error": str(exc),
            }

        # ======================================================
        # 5. RESULTADOS DO ANALYZER
        # ======================================================

        analyses = self._safe_list(
            analyzer_result.get(
                "analyses",
                [],
            )
        )

        value_bets = self._safe_list(
            analyzer_result.get(
                "value_bets",
                [],
            )
        )

        analyzer_summary = self._safe_dict(
            analyzer_result.get(
                "summary",
                {},
            )
        )

        # ======================================================
        # 6. VALUE BETS
        # ======================================================

        try:

            value_bets = analyzer.filter_value_bets(
                analyses
            )

            value_bets = self._safe_list(
                value_bets
            )

        except Exception as exc:

            error(
                "Erro ao filtrar Value Bets: "
                f"{exc}"
            )

            value_bets = []

        # ======================================================
        # 7. MELHORES OPORTUNIDADES
        # ======================================================

        try:

            best_opportunities = (
                analyzer.best_opportunities(
                    analyses,
                    limit=20,
                )
            )

            best_opportunities = (
                self._safe_list(
                    best_opportunities
                )
            )

        except Exception as exc:

            error(
                "Erro ao obter melhores "
                f"oportunidades: {exc}"
            )

            best_opportunities = []

        # ======================================================
        # 8. MELHOR VALUE BET
        # ======================================================

        best_value_bet: Optional[
            Dict[str, Any]
        ] = None

        if value_bets:

            best_value_bet = deepcopy(
                value_bets[0]
            )

        # ======================================================
        # 9. MELHOR OPORTUNIDADE GERAL
        # ======================================================

        best_match: Optional[
            Dict[str, Any]
        ] = None

        if analyses:

            try:

                ordered = sorted(
                    analyses,
                    key=lambda item: float(
                        item.get(
                            "oddreal_index",
                            0,
                        )
                        or 0
                    ),
                    reverse=True,
                )

                if ordered:

                    best_match = deepcopy(
                        ordered[0]
                    )

            except Exception as exc:

                error(
                    "Erro ao identificar "
                    f"melhor oportunidade: {exc}"
                )

        # ======================================================
        # 10. RESUMO DA ANÁLISE
        # ======================================================

        try:

            analysis_summary = analyzer.summary(
                analyses
            )

            analysis_summary = (
                self._safe_dict(
                    analysis_summary
                )
            )

        except Exception as exc:

            error(
                "Erro ao gerar resumo "
                f"da análise: {exc}"
            )

            analysis_summary = (
                analyzer_summary
            )

        # ======================================================
        # 11. DADOS PARA IA
        # ======================================================

        try:

            ai_data = (
                data_manager.prepare_for_ai(
                    analyses
                )
            )

            ai_data = self._safe_list(
                ai_data
            )

        except Exception as exc:

            error(
                "Erro ao preparar dados "
                f"para IA: {exc}"
            )

            ai_data = []

        # ======================================================
        # 12. RESUMO DO DATAMANAGER
        # ======================================================

        data_summary = self._safe_dict(
            managed_data.get(
                "summary",
                {},
            )
        )

        # ======================================================
        # 13. RESULTADO FINAL
        # ======================================================

        result: Dict[str, Any] = {

            # --------------------------------------------------
            # DADOS ORIGINAIS
            # --------------------------------------------------

            "raw_events": deepcopy(
                raw_events
            ),

            # --------------------------------------------------
            # DADOS PROCESSADOS
            # --------------------------------------------------

            "clean_events": deepcopy(
                clean_events
            ),

            "analysis_events": deepcopy(
                analysis_events
            ),

            "analysis_records": deepcopy(
                analysis_records
            ),

            # --------------------------------------------------
            # EVENTOS PREPARADOS
            # --------------------------------------------------

            "events": deepcopy(
                self._prepare_events(
                    analysis_events
                )
            ),

            # --------------------------------------------------
            # ANÁLISES
            # --------------------------------------------------

            "analyses": deepcopy(
                analyses
            ),

            # --------------------------------------------------
            # VALUE BETS
            # --------------------------------------------------

            "value_bets": deepcopy(
                value_bets
            ),

            # --------------------------------------------------
            # MELHORES OPORTUNIDADES
            # --------------------------------------------------

            "best_opportunities": deepcopy(
                best_opportunities
            ),

            "best_match": deepcopy(
                best_match
            ),

            "best_value_bet": deepcopy(
                best_value_bet
            ),

            # --------------------------------------------------
            # IA
            # --------------------------------------------------

            "ai_data": deepcopy(
                ai_data
            ),

            # --------------------------------------------------
            # RESUMOS
            # --------------------------------------------------

            "data_summary": deepcopy(
                data_summary
            ),

            "analysis_summary": deepcopy(
                analysis_summary
            ),

            # --------------------------------------------------
            # CONTADORES
            # --------------------------------------------------

            "total_raw_events": len(
                raw_events
            ),

            "total_clean_events": len(
                clean_events
            ),

            "total_analysis_events": len(
                analysis_events
            ),

            "total_analysis_records": len(
                analysis_records
            ),

            "total_events": len(
                analyses
            ),

            "total_analyses": len(
                analyses
            ),

            "total_value_bets": len(
                value_bets
            ),

            "total_best_opportunities": len(
                best_opportunities
            ),
        }

        # ======================================================
        # ERRO DO ANALYZER
        # ======================================================

        if analyzer_result.get("error"):

            result[
                "analyzer_error"
            ] = analyzer_result.get(
                "error"
            )

        # ======================================================
        # LOG FINAL
        # ======================================================

        info(
            "Pipeline concluído: "
            f"{len(raw_events)} eventos brutos, "
            f"{len(clean_events)} eventos limpos, "
            f"{len(analyses)} análises, "
            f"{len(value_bets)} Value Bets."
        )

        return result

    # ==========================================================
    # ATALHO
    # ==========================================================

    def run(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Alias de execute().
        """

        return self.execute(
            force_refresh=force_refresh
        )


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

pipeline = Pipeline()


# ==========================================================
# EXPORTAÇÃO
# ==========================================================

__all__ = [
    "Pipeline",
    "pipeline",
        ]
