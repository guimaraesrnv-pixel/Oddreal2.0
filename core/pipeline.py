"""
OddReal 2.0
Pipeline Principal

Fluxo:

The Odds API
    ↓
API Client
    ↓
Pipeline
    ↓
Normalização das odds
    ↓
Analyzer
    ↓
OddsEngine
    ↓
Value Bets
    ↓
Dashboard
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.api_client import api_client
from core.analyzer import analyzer
from modules.logger import info, error


class Pipeline:
    """
    Orquestra o processamento completo dos eventos.

    O Pipeline é responsável por transformar a resposta
    bruta da The Odds API em uma estrutura compatível
    com o Analyzer e o OddsEngine.
    """

    def __init__(self) -> None:

        info(
            "Pipeline OddReal 2.0 iniciado."
        )

    # ==========================================================
    # NORMALIZAÇÃO DAS ODDS
    # ==========================================================

    def _extract_best_odd(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Procura a melhor odd disponível nos bookmakers.

        A resposta da The Odds API possui uma estrutura
        diferente daquela utilizada internamente pelo
        OddsEngine.

        Este método faz essa ponte.
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

        best: Optional[Dict[str, Any]] = None

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            bookmaker_name = bookmaker.get(
                "title",
                bookmaker.get(
                    "key",
                    "Desconhecida",
                ),
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

                    odd = outcome.get(
                        "price"
                    )

                    if odd is None:
                        continue

                    try:

                        odd = float(
                            odd
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

                    if odd <= 0:
                        continue

                    candidate = {

                        "odd": odd,

                        "bookmaker": (
                            bookmaker_name
                        ),

                        "market": market.get(
                            "key",
                            "unknown",
                        ),

                        "outcome": outcome.get(
                            "name",
                            "unknown",
                        ),

                    }

                    if (
                        best is None
                        or odd > best["odd"]
                    ):

                        best = candidate

        return best

    # ==========================================================
    # COLETA DAS ODDS DO MERCADO
    # ==========================================================

    def _extract_market_odds(
        self,
        event: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Extrai todas as odds encontradas no evento.

        A estrutura é simplificada para permitir que o
        OddsEngine calcule indicadores de mercado.
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

        odds: List[Dict[str, Any]] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            bookmaker_name = bookmaker.get(
                "title",
                bookmaker.get(
                    "key",
                    "Desconhecida",
                ),
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

                    if price is None:
                        continue

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

                            "market": market.get(
                                "key",
                                "unknown",
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
    ) -> Optional[Dict[str, Any]]:
        """
        Prepara um evento bruto da API para o Analyzer.
        """

        if not isinstance(
            event,
            dict,
        ):
            return None

        best_odd = self._extract_best_odd(
            event
        )

        if best_odd is None:

            return None

        market_odds = self._extract_market_odds(
            event
        )

        prepared = {

            **event,

            "best_odd": best_odd,

            "market_odds": market_odds,

            "bookmakers": market_odds,

        }

        return prepared

    # ==========================================================
    # PREPARAÇÃO DE TODOS OS EVENTOS
    # ==========================================================

    def _prepare_events(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Prepara todos os eventos recebidos da API.
        """

        prepared_events = []

        for event in events:

            try:

                prepared = self._prepare_event(
                    event
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
    # EXECUÇÃO PRINCIPAL
    # ==========================================================

    def execute(self) -> Dict[str, Any]:
        """
        Executa o fluxo completo do OddReal.
        """

        try:

            raw_events = (
                api_client.get_events()
            )

        except Exception as exc:

            error(
                "Erro na coleta de eventos: "
                f"{exc}"
            )

            raw_events = []

        if not isinstance(
            raw_events,
            list,
        ):

            raw_events = []

        events = self._prepare_events(
            raw_events
        )

        analyses = analyzer.analyze(
            events
        )

        value_bets = analyzer.value_bets(
            analyses
        )

        best_match = (
            analyzer.best_opportunity(
                analyses
            )
        )

        info(
            "Pipeline concluído: "
            f"{len(events)} eventos preparados, "
            f"{len(analyses)} análises e "
            f"{len(value_bets)} Value Bets."
        )

        return {

            "events": events,

            "raw_events": raw_events,

            "analyses": analyses,

            "value_bets": value_bets,

            "best_match": best_match,

            "total_events": len(events),

            "total_analyses": len(
                analyses
            ),

            "total_value_bets": len(
                value_bets
            ),

        }


pipeline = Pipeline()
