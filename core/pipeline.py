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
Analyzer
    ↓
Value Bets / EV
    ↓
OddsEngine / IA
    ↓
Dashboard

Responsabilidade deste módulo:
- Orquestrar o fluxo completo;
- Não realizar cálculos quantitativos próprios;
- Preservar os dados recebidos;
- Entregar os dados do DataManager ao Analyzer;
- Consolidar o resultado final;
- Não duplicar a lógica de EV ou Value Bets.

IMPORTANTE:

A lógica quantitativa pertence ao Analyzer.

O Pipeline NÃO deve calcular:
- EV;
- probabilidade;
- odd média;
- margem;
- Value Bet;
- Índice OddReal;
- confiança;
- risco.

Essas responsabilidades pertencem ao Analyzer.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from services.api_client import api_client
from modules.data_manager import data_manager
from modules.analyzer import analyzer
from modules.logger import info, warning, error


class Pipeline:
    """
    Orquestra o processamento completo do OddReal 2.0.

    O Pipeline funciona como camada de integração entre:

        API Client
            ↓
        DataManager
            ↓
        Analyzer
            ↓
        Dashboard / IA / OddsEngine

    Não contém cálculos quantitativos próprios.
    """

    # ==========================================================
    # INICIALIZAÇÃO
    # ==========================================================

    def __init__(self) -> None:

        info(
            "Pipeline OddReal 2.0 iniciado."
        )

    # ==========================================================
    # VALIDAÇÃO
    # ==========================================================

    @staticmethod
    def _ensure_list(
        value: Any,
    ) -> List[Dict[str, Any]]:
        """
        Garante que o valor seja uma lista de dicionários.

        Não altera os objetos recebidos.
        """

        if not isinstance(
            value,
            list,
        ):
            return []

        result: List[
            Dict[str, Any]
        ] = []

        for item in value:

            if isinstance(
                item,
                dict,
            ):

                result.append(
                    item
                )

        return result

    @staticmethod
    def _ensure_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Garante que o valor seja um dicionário.
        """

        if not isinstance(
            value,
            dict,
        ):
            return {}

        return value

    # ==========================================================
    # EXECUÇÃO PRINCIPAL
    # ==========================================================

    def execute(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Executa o pipeline completo.

        Fluxo:

        1. API Client
        2. DataManager
        3. Analyzer
        4. Value Bets
        5. Resumos
        6. Dados para IA
        7. Resultado final

        A lógica quantitativa é executada exclusivamente
        pelo Analyzer.
        """

        # ======================================================
        # 1. COLETA DA API
        # ======================================================

        try:

            raw_events = (
                api_client.get_events(
                    force_refresh=force_refresh
                )
            )

        except Exception as exc:

            error(
                "Erro na coleta da API: "
                f"{exc}"
            )

            raw_events = []

        raw_events = self._ensure_list(
            raw_events
        )

        info(
            "Pipeline recebeu "
            f"{len(raw_events)} eventos "
            "da API."
        )

        # ======================================================
        # 2. DATAMANAGER
        # ======================================================

        try:

            managed_data = (
                data_manager.process(
                    raw_events
                )
            )

            managed_data = (
                self._ensure_dict(
                    managed_data
                )
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
        # DADOS DO DATAMANAGER
        # ======================================================

        manager_raw_events = (
            self._ensure_list(
                managed_data.get(
                    "raw_events",
                    raw_events,
                )
            )
        )

        manager_clean_events = (
            self._ensure_list(
                managed_data.get(
                    "clean_events",
                    [],
                )
            )
        )

        manager_analysis_events = (
            self._ensure_list(
                managed_data.get(
                    "analysis_events",
                    [],
                )
            )
        )

        manager_analysis_records = (
            self._ensure_list(
                managed_data.get(
                    "analysis_records",
                    [],
                )
            )
        )

        data_summary = (
            self._ensure_dict(
                managed_data.get(
                    "summary",
                    {},
                )
            )
        )

        info(
            "Pipeline recebeu do "
            "DataManager: "
            f"{len(manager_analysis_events)} "
            "eventos preparados e "
            f"{len(manager_analysis_records)} "
            "registros de odds."
        )

        # ======================================================
        # 3. ANALYZER
        # ======================================================
        #
        # IMPORTANTE:
        #
        # O Analyzer possui:
        #
        #     process()
        #
        #     analyze_records()
        #
        #     analyze_events()
        #
        #     analyze_data_manager_output()
        #
        # Não possui:
        #
        #     analyze()
        #
        # Portanto o Pipeline utiliza a interface
        # pública correta:
        #
        #     analyzer.process(managed_data)
        #
        # Isso mantém a lógica de análise dentro
        # do Analyzer.
        # ======================================================

        try:

            analyzer_result = (
                analyzer.process(
                    managed_data
                )
            )

            analyzer_result = (
                self._ensure_dict(
                    analyzer_result
                )
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

                "error": str(
                    exc
                ),
            }

        # ======================================================
        # 4. RESULTADOS DO ANALYZER
        # ======================================================

        analyses = (
            self._ensure_list(
                analyzer_result.get(
                    "analyses",
                    [],
                )
            )
        )

        value_bets = (
            self._ensure_list(
                analyzer_result.get(
                    "value_bets",
                    [],
                )
            )
        )

        analysis_summary = (
            self._ensure_dict(
                analyzer_result.get(
                    "summary",
                    {},
                )
            )
        )

        analyzer_processed_at = (
            analyzer_result.get(
                "processed_at"
            )
        )

        analyzer_error = (
            analyzer_result.get(
                "error"
            )
        )

        # ======================================================
        # 5. MELHOR OPORTUNIDADE
        # ======================================================
        #
        # O Analyzer retorna Value Bets ordenadas
        # por Índice OddReal através de:
        #
        #     best_opportunities()
        #
        # O primeiro elemento é, portanto,
        # a melhor oportunidade entre as Value Bets
        # retornadas pelo Analyzer.
        #
        # Não recalculamos nada aqui.
        # ======================================================

        best_value_bet = None

        if value_bets:

            best_value_bet = deepcopy(
                value_bets[0]
            )

        # ======================================================
        # 6. MELHOR ANÁLISE GERAL
        # ======================================================
        #
        # Caso não exista Value Bet, podemos ainda
        # disponibilizar a melhor análise geral
        # pelo Índice OddReal.
        #
        # Esta ordenação é apenas organização do resultado.
        # O cálculo do índice continua sendo responsabilidade
        # do Analyzer.
        # ======================================================

        best_match = None

        if analyses:

            ranked_analyses = sorted(
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

            if ranked_analyses:

                best_match = deepcopy(
                    ranked_analyses[0]
                )

        # ======================================================
        # 7. DADOS PARA IA
        # ======================================================
        #
        # O DataManager já possui prepare_for_ai().
        #
        # Portanto utilizamos a estrutura produzida
        # pelo Analyzer.
        # ======================================================

        try:

            ai_data = (
                data_manager.prepare_for_ai(
                    analyses
                )
            )

            ai_data = (
                self._ensure_list(
                    ai_data
                )
            )

        except Exception as exc:

            error(
                "Erro ao preparar dados "
                f"para IA: {exc}"
            )

            ai_data = []

        # ======================================================
        # 8. CONTADORES
        # ======================================================

        total_events = len(
            manager_analysis_events
        )

        total_records = len(
            manager_analysis_records
        )

        total_analyses = len(
            analyses
        )

        total_value_bets = len(
            value_bets
        )

        # ======================================================
        # 9. LOG DIAGNÓSTICO
        # ======================================================

        info(
            "Pipeline Analyzer: "
            f"{total_records} registros → "
            f"{total_analyses} análises → "
            f"{total_value_bets} Value Bets."
        )

        if total_records > 0 and total_analyses == 0:

            warning(
                "DataManager entregou "
                f"{total_records} registros de odds, "
                "mas o Analyzer não produziu análises."
            )

        if (
            total_analyses > 0
            and total_value_bets == 0
        ):

            info(
                "Analyzer produziu "
                f"{total_analyses} análises, "
                "mas nenhuma foi classificada "
                "como Value Bet."
            )

        if analyzer_error:

            error(
                "Analyzer retornou erro: "
                f"{analyzer_error}"
            )

        # ======================================================
        # 10. RESULTADO FINAL
        # ======================================================

        result: Dict[
            str,
            Any,
        ] = {

            # --------------------------------------------------
            # API
            # --------------------------------------------------

            "raw_events": deepcopy(
                raw_events
            ),

            # --------------------------------------------------
            # DATAMANAGER
            # --------------------------------------------------

            "clean_events": deepcopy(
                manager_clean_events
            ),

            "analysis_events": deepcopy(
                manager_analysis_events
            ),

            "analysis_records": deepcopy(
                manager_analysis_records
            ),

            "data_summary": deepcopy(
                data_summary
            ),

            # --------------------------------------------------
            # ANALYZER
            # --------------------------------------------------

            "analyses": deepcopy(
                analyses
            ),

            "analysis_summary": deepcopy(
                analysis_summary
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
            # CONTADORES
            # --------------------------------------------------

            "total_events": (
                total_events
            ),

            "total_records": (
                total_records
            ),

            "total_analyses": (
                total_analyses
            ),

            "total_value_bets": (
                total_value_bets
            ),

            # --------------------------------------------------
            # CONTROLE
            # --------------------------------------------------

            "processed_at": (
                analyzer_processed_at
            ),

            "error": analyzer_error,
        }

        # ======================================================
        # LOG FINAL
        # ======================================================

        info(
            "Pipeline concluído: "
            f"{total_events} eventos, "
            f"{total_records} registros, "
            f"{total_analyses} análises e "
            f"{total_value_bets} Value Bets."
        )

        return result


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
