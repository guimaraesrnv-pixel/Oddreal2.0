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
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.api_client import api_client
from modules.data_manager import data_manager
from modules.logger import info, error
from core.analyzer import analyzer


class Pipeline:
    """
    Orquestra o processamento completo do OddReal.
    """

    def __init__(self) -> None:

        info(
            "Pipeline OddReal 2.0 iniciado."
        )

    # ==========================================================
    # EXTRAÇÃO DA MELHOR ODD
    # ==========================================================

    def _extract_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

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
                    "title",
                    bookmaker.get(
                        "key",
                        "Desconhecida",
                    ),
                )
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

                market_name = market.get(
                    "key",
                    "unknown",
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

                    price = outcome.get(
                        "price"
                    )

                    try:

                        price = float(
                            price
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

                    if price <= 0:

                        continue

                    candidate = {

                        "odd": price,

                        "bookmaker": (
                            bookmaker_name
                        ),

                        "market": (
                            market_name
                        ),

                        "outcome": outcome.get(
                            "name",
                            "unknown",
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
                    "title",
                    bookmaker.get(
                        "key",
                        "Desconhecida",
                    ),
                )
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

                market_name = market.get(
                    "key",
                    "unknown",
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

                    price = outcome.get(
                        "price"
                    )

                    try:

                        price = float(
                            price
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

                    if price <= 0:

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

                            "outcome": outcome.get(
                                "name",
                                "unknown",
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

        if not isinstance(
            event,
            dict,
        ):

            return None

        best_odd = (
            self._extract_best_odd(
                event
            )
        )

        if best_odd is None:

            return None

        market_odds = (
            self._extract_market_odds(
                event
            )
        )

        if not market_odds:

            return None

        return {

            **event,

            "best_odd": best_odd,

            "market_odds": market_odds,

            "bookmakers": market_odds,

        }

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
        """

        # ------------------------------------------------------
        # 1. COLETA
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # 2. DATA MANAGER
        # ------------------------------------------------------

        try:

            managed_data = (
                data_manager.process(
                    raw_events
                )
            )

            clean_events = (
                managed_data.get(
                    "analysis_events",
                    [],
                )
            )

        except Exception as exc:

            error(
                "Erro no DataManager: "
                f"{exc}"
            )

            clean_events = []

            managed_data = {

                "raw_events": raw_events,

                "clean_events": [],

                "analysis_events": [],

                "summary": {},

            }

        # ------------------------------------------------------
        # 3. NORMALIZAÇÃO DAS ODDS
        # ------------------------------------------------------

        events = (
            self._prepare_events(
                clean_events
            )
        )

        # ------------------------------------------------------
        # 4. ANÁLISE
        # ------------------------------------------------------

        try:

            analyses = analyzer.analyze(
                events
            )

        except Exception as exc:

            error(
                "Erro no Analyzer: "
                f"{exc}"
            )

            analyses = []

        # ------------------------------------------------------
        # 5. VALUE BETS
        # ------------------------------------------------------

        try:

            value_bets = (
                analyzer.value_bets(
                    analyses
                )
            )

        except Exception as exc:

            error(
                "Erro ao identificar "
                f"Value Bets: {exc}"
            )

            value_bets = []

        # ------------------------------------------------------
        # 6. MELHOR OPORTUNIDADE
        # ------------------------------------------------------

        try:

            best_match = (
                analyzer.best_opportunity(
                    analyses
                )
            )

            best_value_bet = (
                analyzer.best_value_bet(
                    analyses
                )
            )

        except Exception as exc:

            error(
                "Erro ao identificar "
                f"melhores oportunidades: {exc}"
            )

            best_match = None

            best_value_bet = None

        # ------------------------------------------------------
        # 7. RESUMO
        # ------------------------------------------------------

        try:

            analysis_summary = (
                analyzer.summary(
                    analyses
                )
            )

        except Exception:

            analysis_summary = {}

        # ------------------------------------------------------
        # 8. DADOS PARA IA
        # ------------------------------------------------------

        try:

            ai_data = (
                data_manager.prepare_for_ai(
                    analyses
                )
            )

        except Exception as exc:

            error(
                "Erro ao preparar dados "
                f"para IA: {exc}"
            )

            ai_data = []

        # ------------------------------------------------------
        # 9. RESULTADO FINAL
        # ------------------------------------------------------

        result = {

            "events": events,

            "raw_events": raw_events,

            "clean_events": (
                managed_data.get(
                    "clean_events",
                    [],
                )
            ),

            "analyses": analyses,

            "value_bets": value_bets,

            "best_match": best_match,

            "best_value_bet": (
                best_value_bet
            ),

            "ai_data": ai_data,

            "data_summary": (
                managed_data.get(
                    "summary",
                    {},
                )
            ),

            "analysis_summary": (
                analysis_summary
            ),

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

        info(
            "Pipeline concluído: "
            f"{len(events)} eventos, "
            f"{len(analyses)} análises e "
            f"{len(value_bets)} Value Bets."
        )

        return result


pipeline = Pipeline()
