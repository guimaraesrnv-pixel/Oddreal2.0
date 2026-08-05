"""
OddReal 2.0
Data Manager

Camada responsável por receber os dados da API,
limpar, validar, normalizar e preparar os eventos
para o Core Analyzer.

Fluxo:

The Odds API
    ↓
DataManager
    ↓
bookmakers autorizados
    ↓
market_odds normalizado
    ↓
Core Analyzer

Este módulo NÃO:
- calcula EV;
- calcula Value Bet;
- calcula Índice OddReal;
- utiliza IA;
- utiliza Streamlit.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.bookmakers import (
    ALLOWED_BOOKMAKERS,
    normalize_bookmaker_name,
    bookmaker_display_name,
)

from modules.logger import info, error


class DataManager:
    """
    Gerenciador central dos dados recebidos da API.
    """

    def __init__(self) -> None:

        self.last_raw_events: List[
            Dict[str, Any]
        ] = []

        self.last_clean_events: List[
            Dict[str, Any]
        ] = []

        self.last_processed_at: Optional[
            str
        ] = None

        info(
            "DataManager OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:

        if value is None:
            return default

        try:
            result = str(
                value
            ).strip()

        except Exception:
            return default

        return (
            result
            if result
            else default
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: Optional[float] = None,
    ) -> Optional[float]:

        if value is None:
            return default

        try:
            result = float(
                value
            )

            if result != result:
                return default

            if result in (
                float("inf"),
                float("-inf"),
            ):
                return default

            return result

        except (
            TypeError,
            ValueError,
        ):
            return default

    # ==========================================================
    # BOOKMAKER
    # ==========================================================

    @staticmethod
    def _normalize_bookmaker(
        bookmaker: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Normaliza um bookmaker da The Odds API.

        Retorna None quando a casa não está
        na whitelist do OddReal.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return None

        raw_key = DataManager._safe_string(
            bookmaker.get(
                "key"
            )
        )

        raw_title = DataManager._safe_string(
            bookmaker.get(
                "title"
            )
        )

        # ------------------------------------------------------
        # Tentamos primeiro a key.
        # Depois o title.
        # ------------------------------------------------------

        normalized = ""

        if raw_key:

            try:
                normalized = (
                    normalize_bookmaker_name(
                        raw_key
                    )
                    or ""
                )
            except Exception:
                normalized = ""

        if (
            not normalized
            and raw_title
        ):

            try:
                normalized = (
                    normalize_bookmaker_name(
                        raw_title
                    )
                    or ""
                )
            except Exception:
                normalized = ""

        normalized = (
            DataManager._safe_string(
                normalized
            )
        )

        # ------------------------------------------------------
        # Verificação da whitelist
        # ------------------------------------------------------

        allowed = False

        if normalized in ALLOWED_BOOKMAKERS:
            allowed = True

        # Compatibilidade caso o normalizador
        # retorne outra forma da key.
        if raw_key in ALLOWED_BOOKMAKERS:
            normalized = raw_key
            allowed = True

        if not allowed:
            return None

        # ------------------------------------------------------
        # Nome para exibição
        # ------------------------------------------------------

        display_name = raw_title

        try:

            display_name = (
                bookmaker_display_name(
                    normalized
                )
                or raw_title
                or normalized
            )

        except Exception:

            display_name = (
                raw_title
                or normalized
            )

        return {
            "key": normalized,
            "title": DataManager._safe_string(
                display_name,
                normalized,
            ),
            "original_key": raw_key,
            "original_title": raw_title,
        }

    # ==========================================================
    # MERCADOS
    # ==========================================================

    def _extract_market_odds(
        self,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Converte a estrutura original da
        The Odds API para a estrutura usada
        pelo Core Analyzer.

        Entrada esperada:

        bookmakers
            └── markets
                 └── outcomes

        Saída:

        [
            {
                "market": "h2h",
                "outcome": "Team A",
                "bookmaker": "bet365",
                "odd": 2.10
            }
        ]
        """

        market_odds: List[
            Dict[str, Any]
        ] = []

        if not isinstance(
            bookmakers,
            list,
        ):
            return market_odds

        for bookmaker in bookmakers:

            normalized_bookmaker = (
                self._normalize_bookmaker(
                    bookmaker
                )
            )

            if normalized_bookmaker is None:
                continue

            bookmaker_key = (
                normalized_bookmaker[
                    "key"
                ]
            )

            bookmaker_title = (
                normalized_bookmaker[
                    "title"
                ]
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

                market_key = (
                    self._safe_string(
                        market.get(
                            "key"
                        )
                    )
                )

                if not market_key:
                    continue

                # --------------------------------------------------
                # ODDREAL trabalha inicialmente com os mercados
                # principais.
                # --------------------------------------------------

                if market_key not in {
                    "h2h",
                    "totals",
                    "spreads",
                }:
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

                    outcome_name = (
                        self._safe_string(
                            outcome.get(
                                "name"
                            )
                        )
                    )

                    if not outcome_name:
                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price"
                        )
                    )

                    if price is None:
                        continue

                    if price <= 1.0:
                        continue

                    record: Dict[
                        str,
                        Any
                    ] = {
                        "market": market_key,

                        "outcome": outcome_name,

                        "name": outcome_name,

                        "bookmaker": bookmaker_title,

                        "bookmaker_key":
                            bookmaker_key,

                        "odd": round(
                            price,
                            6,
                        ),

                        "price": round(
                            price,
                            6,
                        ),
                    }

                    # --------------------------------------------------
                    # Totals / spreads podem possuir ponto.
                    # --------------------------------------------------

                    if "point" in outcome:

                        point = (
                            self._safe_float(
                                outcome.get(
                                    "point"
                                )
                            )
                        )

                        if point is not None:

                            record[
                                "point"
                            ] = point

                    market_odds.append(
                        record
                    )

        return market_odds

    # ==========================================================
    # BOOKMAKERS NORMALIZADOS
    # ==========================================================

    def _clean_bookmakers(
        self,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Mantém somente bookmakers autorizados.

        A estrutura interna original é preservada,
        mas os nomes principais são normalizados.
        """

        cleaned: List[
            Dict[str, Any]
        ] = []

        if not isinstance(
            bookmakers,
            list,
        ):
            return cleaned

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            normalized = (
                self._normalize_bookmaker(
                    bookmaker
                )
            )

            if normalized is None:
                continue

            copy_bookmaker = deepcopy(
                bookmaker
            )

            copy_bookmaker[
                "_oddreal_key"
            ] = normalized[
                "key"
            ]

            copy_bookmaker[
                "_oddreal_title"
            ] = normalized[
                "title"
            ]

            cleaned.append(
                copy_bookmaker
            )

        return cleaned

    # ==========================================================
    # VALIDAÇÃO
    # ==========================================================

    def validate_event(
        self,
        event: Dict[str, Any],
    ) -> bool:

        if not isinstance(
            event,
            dict,
        ):
            return False

        event_id = event.get(
            "id"
        )

        home_team = event.get(
            "home_team"
        )

        away_team = event.get(
            "away_team"
        )

        if not event_id:
            return False

        if not home_team:
            return False

        if not away_team:
            return False

        return True

    # ==========================================================
    # LIMPEZA DE EVENTO
    # ==========================================================

    def clean_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Limpa um evento e cria market_odds.
        """

        if not self.validate_event(
            event
        ):
            return None

        cleaned = deepcopy(
            event
        )

        # ------------------------------------------------------
        # DADOS BÁSICOS
        # ------------------------------------------------------

        cleaned["id"] = (
            self._safe_string(
                event.get(
                    "id"
                )
            )
        )

        cleaned["sport_key"] = (
            self._safe_string(
                event.get(
                    "sport_key"
                ),
                "unknown",
            )
        )

        cleaned["sport_title"] = (
            self._safe_string(
                event.get(
                    "sport_title"
                ),
                cleaned[
                    "sport_key"
                ],
            )
        )

        cleaned["home_team"] = (
            self._safe_string(
                event.get(
                    "home_team"
                ),
                "Mandante",
            )
        )

        cleaned["away_team"] = (
            self._safe_string(
                event.get(
                    "away_team"
                ),
                "Visitante",
            )
        )

        cleaned["commence_time"] = (
            self._safe_string(
                event.get(
                    "commence_time"
                )
            )
        )

        # ------------------------------------------------------
        # ==========================================================
# BOOKMAKERS
# ==========================================================

original_bookmakers = event.get(
    "bookmakers",
    [],
)

if not isinstance(
    original_bookmakers,
    list,
):
    original_bookmakers = []

info(
    f"Evento "
    f"{cleaned['home_team']} x "
    f"{cleaned['away_team']} "
    f"recebeu "
    f"{len(original_bookmakers)} "
    f"bookmakers da API."
)

for bookmaker in original_bookmakers:

    if isinstance(
        bookmaker,
        dict,
    ):

        info(
            "Bookmaker recebido: "
            f"key={bookmaker.get('key', '')} | "
            f"title={bookmaker.get('title', '')}"
        )

# ----------------------------------------------------------
# TEMPORARIAMENTE: preserva os bookmakers recebidos
# ----------------------------------------------------------

cleaned["bookmakers"] = (
    deepcopy(
        original_bookmakers
    )
)

        # ------------------------------------------------------
        # MARKET ODDS
        # ------------------------------------------------------

        cleaned[
            "market_odds"
        ] = self._extract_market_odds(
            original_bookmakers
        )

        # ------------------------------------------------------
        # INFORMAÇÕES ÚTEIS
        # ------------------------------------------------------

        cleaned[
            "allowed_bookmakers"
        ] = sorted(
            set(
                item[
                    "_oddreal_key"
                ]
                for item
                in cleaned_bookmakers
                if isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "_oddreal_key"
                )
            )
        )

        cleaned[
            "bookmaker_count"
        ] = len(
            cleaned_bookmakers
        )

        cleaned[
            "market_odds_count"
        ] = len(
            cleaned[
                "market_odds"
            ]
        )

        cleaned[
            "_processed_at"
        ] = self._now_iso()

        return cleaned

    # ==========================================================
    # PROCESSAMENTO EM LOTE
    # ==========================================================

    def clean_events(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            events,
            list,
        ):
            return []

        cleaned_events: List[
            Dict[str, Any]
        ] = []

        for event in events:

            try:

                cleaned = (
                    self.clean_event(
                        event
                    )
                )

                if cleaned is not None:

                    cleaned_events.append(
                        cleaned
                    )

            except Exception as exc:

                error(
                    "Erro ao limpar evento: "
                    f"{exc}"
                )

        self.last_clean_events = (
            deepcopy(
                cleaned_events
            )
        )

        self.last_processed_at = (
            self._now_iso()
        )

        return cleaned_events

    # ==========================================================
    # PREPARAÇÃO PARA ANÁLISE
    # ==========================================================

    def prepare_for_analysis(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Só envia ao Analyzer eventos que possuem:

        - bookmaker autorizado;
        - market_odds válidos.
        """

        cleaned_events = (
            self.clean_events(
                events
            )
        )

        prepared: List[
            Dict[str, Any]
        ] = []

        for event in cleaned_events:

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            market_odds = event.get(
                "market_odds",
                [],
            )

            if not bookmakers:
                continue

            if not market_odds:
                continue

            prepared.append(
                event
            )

        info(
            "DataManager preparou "
            f"{len(prepared)} eventos "
            "para análise."
        )

        # ------------------------------------------------------
        # Diagnóstico
        # ------------------------------------------------------

        total_market_odds = sum(
            len(
                event.get(
                    "market_odds",
                    [],
                )
            )
            for event in prepared
        )

        info(
            "DataManager encontrou "
            f"{total_market_odds} registros "
            "de odds para análise."
        )

        return prepared

    # ==========================================================
    # PREPARAÇÃO PARA IA
    # ==========================================================

    def prepare_for_ai(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            analyses,
            list,
        ):
            return []

        ai_data: List[
            Dict[str, Any]
        ] = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            ai_data.append(
                {
                    "event_id":
                        analysis.get(
                            "id"
                        ),

                    "sport":
                        analysis.get(
                            "sport_title",
                            analysis.get(
                                "sport_key"
                            ),
                        ),

                    "home_team":
                        analysis.get(
                            "home_team"
                        ),

                    "away_team":
                        analysis.get(
                            "away_team"
                        ),

                    "market":
                        analysis.get(
                            "market"
                        ),

                    "outcome":
                        analysis.get(
                            "outcome"
                        ),

                    "bookmaker":
                        analysis.get(
                            "bookmaker"
                        ),

                    "odd":
                        analysis.get(
                            "odd"
                        ),

                    "probability":
                        analysis.get(
                            "probability"
                        ),

                    "expected_value":
                        analysis.get(
                            "expected_value"
                        ),

                    "oddreal_index":
                        analysis.get(
                            "oddreal_index"
                        ),

                    "confidence_level":
                        analysis.get(
                            "confidence_level"
                        ),

                    "average_odd":
                        analysis.get(
                            "average_odd"
                        ),

                    "market_variation":
                        analysis.get(
                            "market_variation"
                        ),

                    "risk":
                        analysis.get(
                            "risk"
                        ),

                    "is_value_bet":
                        analysis.get(
                            "is_value_bet",
                            False,
                        ),
                }
            )

        return ai_data

    # ==========================================================
    # RESUMO
    # ==========================================================

    def summary(
        self,
        events: Optional[
            List[
                Dict[str, Any]
            ]
        ] = None,
    ) -> Dict[str, Any]:

        if events is None:

            events = (
                self.last_clean_events
            )

        if not isinstance(
            events,
            list,
        ):
            events = []

        sports = set()

        total_bookmakers = 0

        total_market_odds = 0

        for event in events:

            if not isinstance(
                event,
                dict,
            ):
                continue

            sport = event.get(
                "sport_title",
                event.get(
                    "sport_key"
                ),
            )

            if sport:
                sports.add(
                    sport
                )

            total_bookmakers += len(
                event.get(
                    "bookmakers",
                    [],
                )
            )

            total_market_odds += len(
                event.get(
                    "market_odds",
                    [],
                )
            )

        return {

            "total_events":
                len(events),

            "total_sports":
                len(sports),

            "sports":
                sorted(sports),

            "total_bookmakers":
                total_bookmakers,

            "total_market_odds":
                total_market_odds,

            "allowed_bookmakers":
                sorted(
                    ALLOWED_BOOKMAKERS
                ),

            "processed_at":
                self.last_processed_at,
        }

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return {

            "raw_events":
                deepcopy(
                    self.last_raw_events
                ),

            "clean_events":
                deepcopy(
                    self.last_clean_events
                ),

            "processed_at":
                self.last_processed_at,

            "summary":
                self.summary(),
        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self,
    ) -> None:

        self.last_raw_events = []

        self.last_clean_events = []

        self.last_processed_at = None

        info(
            "DataManager resetado."
        )

    # ==========================================================
    # CICLO COMPLETO
    # ==========================================================

    def process(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Executa o ciclo completo.

        Mantém os dados brutos,
        limpa os eventos,
        cria market_odds
        e prepara os eventos para análise.
        """

        if not isinstance(
            events,
            list,
        ):
            events = []

        self.last_raw_events = (
            deepcopy(
                events
            )
        )

        clean_events = (
            self.clean_events(
                events
            )
        )

        analysis_events = (
            self.prepare_for_analysis(
                clean_events
            )
        )

        return {

            "raw_events":
                deepcopy(
                    events
                ),

            "clean_events":
                deepcopy(
                    clean_events
                ),

            "analysis_events":
                deepcopy(
                    analysis_events
                ),

            "summary":
                self.summary(
                    clean_events
                ),
        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

data_manager = DataManager()


__all__ = [
    "DataManager",
    "data_manager",
]
                
