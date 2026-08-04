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
Normalização
    ↓
Analyzer
    ↓
OddsEngine
    ↓
Value Bets
    ↓
IA
    ↓
Dashboard

Responsabilidade deste módulo:
- Orquestrar o fluxo completo;
- Não realizar cálculos quantitativos próprios;
- Preservar a estrutura original dos dados;
- Preparar informações para o Analyzer;
- Consolidar o resultado final para o Dashboard.
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
    Orquestra o processamento completo do OddReal 2.0.
    """

    def __init__(self) -> None:

        info(
            "Pipeline OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> Optional[float]:
        """
        Converte um valor para float com segurança.
        """

        try:

            if value is None:
                return None

            result = float(value)

            if result <= 0:
                return None

            return result

        except (
            TypeError,
            ValueError,
        ):

            return None

    # ==========================================================
    # EXTRAÇÃO DA MELHOR ODD
    # ==========================================================

    def _extract_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra a maior odd disponível no evento.

        IMPORTANTE:
        Esta função NÃO altera a estrutura original
        dos bookmakers.
        """

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            return None

        best: Optional[
            Dict[str, Any]
        ] = None

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            bookmaker_name = (
                bookmaker.get(
                    "title"
                )
                or bookmaker.get(
                    "key"
                )
                or "Desconhecida"
            )

            markets = bookmaker.get(
                "markets",
                [],
            )

            if not isinstance(
                markets,
                list,
            ):

                continue

            for market in markets:

                if not isinstance(
                    market,
                    dict,
                ):

                    continue

                market_name = (
                    market.get(
                        "key"
                    )
                    or "unknown"
                )

                outcomes = market.get(
                    "outcomes",
                    [],
                )

                if not isinstance(
                    outcomes,
                    list,
                ):

                    continue

                for outcome in outcomes:

                    if not isinstance(
                        outcome,
                        dict,
                    ):

                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price"
                        )
                    )

                    if price is None:
                        continue

                    candidate = {

                        "odd": price,

                        "bookmaker": (
                            bookmaker_name
                        ),

                        "market": (
                            market_name
                        ),

                        "outcome": (
                            outcome.get(
                                "name",
                                "unknown",
                            )
                        ),

                    }

                    if (
                        best is None
                        or price > best["odd"]
                    ):

                        best = candidate

        return best

    # ==========================================================
    # EXTRAÇÃO DAS ODDS
    # ==========================================================

    def _extract_market_odds(
        self,
        event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Cria uma visão plana das odds disponíveis.

        A estrutura original de bookmakers permanece
        preservada no evento.
        """

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            return []

        odds: List[
            Dict[str, Any]
        ] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            bookmaker_name = (
                bookmaker.get(
                    "title"
                )
                or bookmaker.get(
                    "key"
                )
                or "Desconhecida"
            )

            markets = bookmaker.get(
                "markets",
                [],
            )

            if not isinstance(
                markets,
                list,
            ):

                continue

            for market in markets:

                if not isinstance(
                    market,
                    dict,
                ):

                    continue

                market_name = (
                    market.get(
                        "key"
                    )
                    or "unknown"
                )

                outcomes = market.get(
                    "outcomes",
                    [],
                )

                if not isinstance(
                    outcomes,
                    list,
                ):

                    continue

                for outcome in outcomes:

                    if not isinstance(
                        outcome,
                        dict,
                    ):

                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price"
                        )
                    )

                    if price is None:
                        continue

                    odds.append(
                        {

                            "odd": price,

                            "bookmaker": (
                                bookmaker_name
                            ),

                            "market": (
                                market_name
                            ),

                            "outcome": (
                                outcome.get(
                                    "name",
                                    "unknown",
                                )
                            ),

                        }
                    )

        return odds

    # ==========================================================
    # PREPARAÇÃO DO EVENTO
    # ==========================================================

    def _prepare_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Prepara um evento para o Analyzer.

        NÃO substitui bookmakers.

        São adicionados apenas campos auxiliares:
        - best_odd
        - market_odds
        """

        if not isinstance(
            event,
            dict,
        ):

            return None

        # ------------------------------------------------------
        # MELHOR ODD
        # ------------------------------------------------------

        best_odd = (
            self._extract_best_odd(
                event
            )
        )

        if best_odd is None:

            return None

        # ------------------------------------------------------
        # ODDS PLANAS
        # ------------------------------------------------------

        market_odds = (
            self._extract_market_odds(
                event
            )
        )

        if not market_odds:

            return None

        # ------------------------------------------------------
        # PRESERVAR EVENTO ORIGINAL
        # ------------------------------------------------------

        prepared = deepcopy(
            event
        )

        # ------------------------------------------------------
        # CAMPOS AUXILIARES
        # ------------------------------------------------------

        prepared["best_odd"] = (
            best_odd
        )

        prepared["market_odds"] = (
            market_odds
        )

        # IMPORTANTE:
        # NÃO fazemos:
        #
        # prepared["bookmakers"] = market_odds
        #
        # porque isso destruiria a estrutura
        # original recebida da The Odds API.

        return prepared

    # ==========================================================
    # PREPARAÇÃO DOS EVENTOS
    # ==========================================================

    def _prepare_events(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Prepara todos os eventos válidos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        prepared_events: List[
            Dict[str, Any]
        ] = []

        for event in events:

            try:

                prepared = (
                    self._prepare_event(
                        event
                    )
                )

                if prepared is not None:

                    prepared_events.append(
                        prepared
                    )

            except Exception as exc:

                error(
                    "Erro ao preparar evento: "
                    f"{exc}"
                )

        return prepared_events

    # ==========================================================
    # EXECUÇÃO
    # ==========================================================

    def execute(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Executa todo o pipeline.

        Fluxo:

        API
        ↓
        DataManager
        ↓
        Preparação
        ↓
        Analyzer
        ↓
        Value Bets
        ↓
        Dados para IA
        ↓
        Resultado
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

        if not isinstance(
            raw_events,
            list,
        ):

            raw_events = []

        # ======================================================
        # 2. DATA MANAGER
        # ======================================================

        try:

            managed_data = (
                data_manager.process(
                    raw_events
                )
            )

            if not isinstance(
                managed_data,
                dict,
            ):

                managed_data = {}

            clean_events = (
                managed_data.get(
                    "analysis_events",
                    [],
                )
            )

            if not isinstance(
                clean_events,
                list,
            ):

                clean_events = []

        except Exception as exc:

            error(
                "Erro no DataManager: "
                f"{exc}"
            )

            clean_events = []

            managed_data = {

                "raw_events": (
                    deepcopy(
                        raw_events
                    )
                ),

                "clean_events": [],

                "analysis_events": [],

                "summary": {},

            }

        # ======================================================
        # 3. PREPARAÇÃO DOS EVENTOS
        # ======================================================

        events = (
            self._prepare_events(
                clean_events
            )
        )

        # ======================================================
        # 4. ANALYZER
        # ======================================================

        try:

            analyses = analyzer.analyze(
                events
            )

            if not isinstance(
                analyses,
                list,
            ):

                analyses = []

        except Exception as exc:

            error(
                "Erro no Analyzer: "
                f"{exc}"
            )

            analyses = []

        # ======================================================
        # 5. VALUE BETS
        # ======================================================

        try:

            value_bets = (
                analyzer.value_bets(
                    analyses
                )
            )

            if not isinstance(
                value_bets,
                list,
            ):

                value_bets = []

        except Exception as exc:

            error(
                "Erro ao identificar "
                f"Value Bets: {exc}"
            )

            value_bets = []

        # ======================================================
        # 6. MELHOR OPORTUNIDADE
        # ======================================================

        best_match = None
        best_value_bet = None

        try:

            best_match = (
                analyzer.best_opportunity(
                    analyses
                )
            )

        except Exception as exc:

            error(
                "Erro ao identificar "
                f"melhor oportunidade: {exc}"
            )

        try:

            best_value_bet = (
                analyzer.best_value_bet(
                    analyses
                )
            )

        except Exception as exc:

            error(
                "Erro ao identificar "
                f"melhor Value Bet: {exc}"
            )

        # ======================================================
        # 7. RESUMO DA ANÁLISE
        # ======================================================

        try:

            analysis_summary = (
                analyzer.summary(
                    analyses
                )
            )

            if not isinstance(
                analysis_summary,
                dict,
            ):

                analysis_summary = {}

        except Exception as exc:

            error(
                "Erro ao gerar resumo "
                f"da análise: {exc}"
            )

            analysis_summary = {}

        # ======================================================
        # 8. DADOS PARA IA
        # ======================================================

        try:

            ai_data = (
                data_manager.prepare_for_ai(
                    analyses
                )
            )

            if not isinstance(
                ai_data,
                list,
            ):

                ai_data = []

        except Exception as exc:

            error(
                "Erro ao preparar dados "
                f"para IA: {exc}"
            )

            ai_data = []

        # ======================================================
        # 9. RESUMO DOS DADOS
        # ======================================================

        data_summary = (
            managed_data.get(
                "summary",
                {},
            )
        )

        if not isinstance(
            data_summary,
            dict,
        ):

            data_summary = {}

        # ======================================================
        # 10. RESULTADO FINAL
        # ======================================================

        result: Dict[
            str,
            Any
        ] = {

            # --------------------------------------------------
            # EVENTOS
            # --------------------------------------------------

            "events": deepcopy(
                events
            ),

            "raw_events": deepcopy(
                raw_events
            ),

            "clean_events": deepcopy(
                managed_data.get(
                    "clean_events",
                    [],
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

            "best_match": (
                best_match
            ),

            "best_value_bet": (
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

            "data_summary": (
                data_summary
            ),

            "analysis_summary": (
                analysis_summary
            ),

            # --------------------------------------------------
            # CONTADORES
            # --------------------------------------------------

            "total_events": len(
                events
            ),

            "total_analyses": len(
                analyses
            ),

            "total_value_bets": len(
                value_bets
            ),

        }

        # ======================================================
        # LOG FINAL
        # ======================================================

        info(
            "Pipeline concluído: "
            f"{len(events)} eventos, "
            f"{len(analyses)} análises e "
            f"{len(value_bets)} Value Bets."
        )

        return result


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

pipeline = Pipeline()
