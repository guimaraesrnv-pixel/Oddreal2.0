"""
OddReal 2.0
Gerenciador de Dados

Responsabilidades:
- receber dados da API;
- validar eventos;
- limpar estruturas inválidas;
- padronizar informações;
- preservar dados brutos;
- normalizar bookmakers;
- preservar bookmakers recebidos;
- preparar eventos para análise;
- extrair registros de odds;
- preparar dados para IA;
- fornecer estatísticas básicas.

Este módulo NÃO calcula:
- probabilidade de mercado;
- EV;
- Value Bet;
- Índice OddReal.

Essas responsabilidades permanecem no Analyzer/OddsEngine.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from modules.logger import info, error


# ==========================================================
# BOOKMAKERS
# ==========================================================

try:

    from config.bookmakers import (
        ALLOWED_BOOKMAKERS,
        normalize_bookmaker_name,
        bookmaker_display_name,
    )

except Exception as exc:

    error(
        "Não foi possível carregar config.bookmakers: "
        f"{exc}"
    )

    ALLOWED_BOOKMAKERS = set()

    def normalize_bookmaker_name(
        value: Any,
    ) -> Optional[str]:

        value = str(
            value or ""
        ).strip().lower()

        return value or None

    def bookmaker_display_name(
        value: Any,
    ) -> str:

        return str(
            value or ""
        ).strip()


class DataManager:
    """
    Camada responsável pelo ciclo de vida dos dados.

    IMPORTANTE:

    O DataManager NÃO deve eliminar bookmakers
    simplesmente porque eles não estão na lista
    ALLOWED_BOOKMAKERS.

    A função desta camada é preservar e estruturar
    os dados recebidos da API.

    A seleção dos bookmakers utilizados no cálculo
    estatístico deve ser feita pelo Analyzer/OddsEngine.
    """

    def __init__(self) -> None:

        self.last_raw_events: List[
            Dict[str, Any]
        ] = []

        self.last_clean_events: List[
            Dict[str, Any]
        ] = []

        self.last_analysis_records: List[
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

    @staticmethod
    def _safe_list(
        value: Any,
    ) -> List[Any]:

        if isinstance(
            value,
            list,
        ):

            return value

        return []

    # ==========================================================
    # BOOKMAKERS
    # ==========================================================

    @staticmethod
    def _bookmaker_key(
        bookmaker: Dict[str, Any],
    ) -> str:

        if not isinstance(
            bookmaker,
            dict,
        ):

            return ""

        return DataManager._safe_string(
            bookmaker.get(
                "key"
            )
        )

    @staticmethod
    def _bookmaker_title(
        bookmaker: Dict[str, Any],
    ) -> str:

        if not isinstance(
            bookmaker,
            dict,
        ):

            return ""

        title = DataManager._safe_string(
            bookmaker.get(
                "title"
            )
        )

        if title:
            return title

        return DataManager._safe_string(
            bookmaker.get(
                "key"
            )
        )

    @classmethod
    def _normalized_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> Optional[str]:

        if not isinstance(
            bookmaker,
            dict,
        ):

            return None

        key = cls._bookmaker_key(
            bookmaker
        )

        title = cls._bookmaker_title(
            bookmaker
        )

        normalized = (
            normalize_bookmaker_name(
                key
            )
        )

        if normalized:
            return normalized

        normalized = (
            normalize_bookmaker_name(
                title
            )
        )

        if normalized:
            return normalized

        return None

    @classmethod
    def _is_allowed_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> bool:

        normalized = (
            cls._normalized_bookmaker(
                bookmaker
            )
        )

        if not normalized:
            return False

        return normalized in (
            ALLOWED_BOOKMAKERS
        )

    # ==========================================================
    # MARKET
    # ==========================================================

    @classmethod
    def _clean_market(
        cls,
        market: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not isinstance(
            market,
            dict,
        ):

            return None

        market_key = cls._safe_string(
            market.get(
                "key"
            )
        )

        if not market_key:
            return None

        cleaned_market = deepcopy(
            market
        )

        cleaned_market[
            "key"
        ] = market_key

        cleaned_market[
            "last_update"
        ] = cls._safe_string(
            market.get(
                "last_update"
            )
        )

        outcomes = cls._safe_list(
            market.get(
                "outcomes",
                [],
            )
        )

        cleaned_outcomes: List[
            Dict[str, Any]
        ] = []

        for outcome in outcomes:

            if not isinstance(
                outcome,
                dict,
            ):

                continue

            name = cls._safe_string(
                outcome.get(
                    "name"
                )
            )

            if not name:
                continue

            price = cls._safe_float(
                outcome.get(
                    "price"
                )
            )

            if (
                price is None
                or price <= 1.0
            ):

                continue

            cleaned_outcome = deepcopy(
                outcome
            )

            cleaned_outcome[
                "name"
            ] = name

            cleaned_outcome[
                "price"
            ] = price

            if "point" in outcome:

                point = cls._safe_float(
                    outcome.get(
                        "point"
                    )
                )

                if point is not None:

                    cleaned_outcome[
                        "point"
                    ] = point

            cleaned_outcomes.append(
                cleaned_outcome
            )

        if not cleaned_outcomes:
            return None

        cleaned_market[
            "outcomes"
        ] = cleaned_outcomes

        return cleaned_market

    # ==========================================================
    # BOOKMAKER
    # ==========================================================

    @classmethod
    def _clean_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not isinstance(
            bookmaker,
            dict,
        ):

            return None

        key = cls._bookmaker_key(
            bookmaker
        )

        title = cls._bookmaker_title(
            bookmaker
        )

        if not key and not title:
            return None

        normalized = (
            cls._normalized_bookmaker(
                bookmaker
            )
        )

        cleaned_bookmaker = deepcopy(
            bookmaker
        )

        cleaned_bookmaker[
            "key"
        ] = key

        cleaned_bookmaker[
            "title"
        ] = title

        cleaned_bookmaker[
            "_normalized_key"
        ] = normalized

        cleaned_bookmaker[
            "_display_name"
        ] = (
            bookmaker_display_name(
                normalized
            )
            if normalized
            else (
                title
                or key
            )
        )

        cleaned_bookmaker[
            "_allowed"
        ] = cls._is_allowed_bookmaker(
            bookmaker
        )

        markets = cls._safe_list(
            bookmaker.get(
                "markets",
                [],
            )
        )

        cleaned_markets: List[
            Dict[str, Any]
        ] = []

        for market in markets:

            cleaned_market = (
                cls._clean_market(
                    market
                )
            )

            if cleaned_market is not None:

                cleaned_markets.append(
                    cleaned_market
                )

        cleaned_bookmaker[
            "markets"
        ] = cleaned_markets

        return cleaned_bookmaker

    @classmethod
    def _clean_bookmakers(
        cls,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            bookmakers,
            list,
        ):

            return []

        cleaned: List[
            Dict[str, Any]
        ] = []

        for bookmaker in bookmakers:

            try:

                result = (
                    cls._clean_bookmaker(
                        bookmaker
                    )
                )

                if result is not None:

                    cleaned.append(
                        result
                    )

            except Exception as exc:

                error(
                    "Erro ao limpar bookmaker: "
                    f"{exc}"
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

        event_id = self._safe_string(
            event.get(
                "id"
            )
        )

        home_team = self._safe_string(
            event.get(
                "home_team"
            )
        )

        away_team = self._safe_string(
            event.get(
                "away_team"
            )
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

        if not self.validate_event(
            event
        ):

            return None

        cleaned = deepcopy(
            event
        )

        cleaned[
            "id"
        ] = self._safe_string(
            event.get(
                "id"
            )
        )

        cleaned[
            "sport_key"
        ] = self._safe_string(
            event.get(
                "sport_key"
            ),
            "unknown",
        )

        cleaned[
            "sport_title"
        ] = self._safe_string(
            event.get(
                "sport_title"
            ),
            cleaned[
                "sport_key"
            ],
        )

        cleaned[
            "home_team"
        ] = self._safe_string(
            event.get(
                "home_team"
            ),
            "Mandante",
        )

        cleaned[
            "away_team"
        ] = self._safe_string(
            event.get(
                "away_team"
            ),
            "Visitante",
        )

        cleaned[
            "commence_time"
        ] = self._safe_string(
            event.get(
                "commence_time"
            )
        )

        original_bookmakers = (
            event.get(
                "bookmakers",
                [],
            )
        )

        if not isinstance(
            original_bookmakers,
            list,
        ):

            original_bookmakers = []

        info(
            f"Evento "
            f"{cleaned['home_team']} x "
            f"{cleaned['away_team']} recebeu "
            f"{len(original_bookmakers)} "
            f"bookmakers da API."
        )

        cleaned_bookmakers = (
            self._clean_bookmakers(
                original_bookmakers
            )
        )

        cleaned[
            "bookmakers"
        ] = cleaned_bookmakers

        cleaned[
            "_bookmaker_count"
        ] = len(
            cleaned_bookmakers
        )

        cleaned[
            "_allowed_bookmaker_count"
        ] = sum(
            1
            for bookmaker
            in cleaned_bookmakers
            if bookmaker.get(
                "_allowed",
                False,
            )
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

        self.last_clean_events = deepcopy(
            cleaned_events
        )

        self.last_processed_at = (
            self._now_iso()
        )

        return cleaned_events

    # ==========================================================
    # EXTRAÇÃO DE ODDS
    # ==========================================================

    def extract_odds_records(
        self,
        events: List[
            Dict[str, Any]
        ],
        allowed_only: bool = False,
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            events,
            list,
        ):

            return []

        records: List[
            Dict[str, Any]
        ] = []

        for event in events:

            if not isinstance(
                event,
                dict,
            ):

                continue

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):

                continue

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):

                    continue

                allowed = bookmaker.get(
                    "_allowed",
                    False,
                )

                # IMPORTANTE:
                # O padrão agora é False.
                #
                # Dessa forma o DataManager preserva
                # os bookmakers recebidos pela API.
                #
                # O Analyzer/OddsEngine fará posteriormente
                # a seleção das casas autorizadas para
                # cálculo do consenso.

                if (
                    allowed_only
                    and not allowed
                ):

                    continue

                bookmaker_key = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or normalize_bookmaker_name(
                        bookmaker.get(
                            "key",
                            bookmaker.get(
                                "title",
                                "",
                            ),
                        )
                    )
                )

                if not bookmaker_key:
                    continue

                bookmaker_title = (
                    bookmaker.get(
                        "_display_name"
                    )
                    or bookmaker_display_name(
                        bookmaker_key
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

                    market_key = (
                        self._safe_string(
                            market.get(
                                "key"
                            )
                        )
                    )

                    if not market_key:
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

                        odd = (
                            self._safe_float(
                                outcome.get(
                                    "price"
                                )
                            )
                        )

                        if (
                            not outcome_name
                            or odd is None
                            or odd <= 1.0
                        ):

                            continue

                        record: Dict[
                            str,
                            Any,
                        ] = {

                            "id": event.get(
                                "id"
                            ),

                            "event_id": event.get(
                                "id"
                            ),

                            "sport_key": event.get(
                                "sport_key"
                            ),

                            "sport_title": event.get(
                                "sport_title"
                            ),

                            "home_team": event.get(
                                "home_team"
                            ),

                            "away_team": event.get(
                                "away_team"
                            ),

                            "commence_time": event.get(
                                "commence_time"
                            ),

                            "bookmaker_key": (
                                bookmaker_key
                            ),

                            "bookmaker": (
                                bookmaker_title
                            ),

                            "market_key": (
                                market_key
                            ),

                            "outcome_name": (
                                outcome_name
                            ),

                            "odd": odd,

                            # Preserva informação de
                            # autorização para o Analyzer.
                            "bookmaker_allowed": bool(
                                allowed
                            ),
                        }

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

                        records.append(
                            record
                        )

        self.last_analysis_records = (
            deepcopy(
                records
            )
        )

        info(
            "DataManager encontrou "
            f"{len(records)} registros de odds "
            "para análise."
        )

        return records

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

            if not isinstance(
                bookmakers,
                list,
            ):

                continue

            usable_bookmakers = []

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):

                    continue

                markets = bookmaker.get(
                    "markets",
                    [],
                )

                if not isinstance(
                    markets,
                    list,
                ):

                    continue

                # O bookmaker continua utilizável
                # mesmo que ainda não tenha sido
                # reconhecido em ALLOWED_BOOKMAKERS.
                #
                # Isso evita que o DataManager destrua
                # os dados recebidos pela API.

                if markets:

                    usable_bookmakers.append(
                        bookmaker
                    )

            if not usable_bookmakers:

                continue

            prepared_event = deepcopy(
                event
            )

            prepared_event[
                "bookmakers"
            ] = usable_bookmakers

            prepared.append(
                prepared_event
            )

        # ======================================================
        # CORREÇÃO PRINCIPAL
        # ======================================================
        #
        # Antes:
        #
        # allowed_only=True
        #
        # Isso fazia o DataManager eliminar os bookmakers
        # antes do Analyzer receber os dados.
        #
        # Agora:
        #
        # allowed_only=False
        #
        # O DataManager preserva os registros.
        # A seleção das casas autorizadas pertence ao
        # Analyzer/OddsEngine.

        records = (
            self.extract_odds_records(
                prepared,
                allowed_only=False,
            )
        )

        info(
            "DataManager preparou "
            f"{len(prepared)} eventos "
            "para análise."
        )

        info(
            "DataManager encontrou "
            f"{len(records)} registros de odds "
            "para análise."
        )

        # Diagnóstico adicional.
        allowed_records = sum(
            1
            for record in records
            if record.get(
                "bookmaker_allowed",
                False,
            )
        )

        info(
            "DataManager identificou "
            f"{allowed_records} registros "
            "pertencentes aos bookmakers "
            "autorizados."
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

        ai_data = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):

                continue

            ai_data.append(
                {

                    "event_id": analysis.get(
                        "event_id",
                        analysis.get(
                            "id"
                        ),
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
                        "market",
                        analysis.get(
                            "market_key"
                        ),
                    ),

                    "outcome": analysis.get(
                        "outcome",
                        analysis.get(
                            "outcome_name"
                        ),
                    ),

                    "bookmaker": analysis.get(
                        "bookmaker"
                    ),

                    "odd": analysis.get(
                        "odd"
                    ),

                    "best_odd": analysis.get(
                        "best_odd"
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

        bookmaker_count = 0
        allowed_bookmaker_count = 0
        odds_count = 0

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

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):

                continue

            bookmaker_count += len(
                bookmakers
            )

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):

                    continue

                if bookmaker.get(
                    "_allowed",
                    False,
                ):

                    allowed_bookmaker_count += 1

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

                    if isinstance(
                        outcomes,
                        list,
                    ):

                        odds_count += len(
                            outcomes
                        )

        return {

            "total_events": len(
                events
            ),

            "total_sports": len(
                sports
            ),

            "sports": sorted(
                sports
            ),

            "total_bookmakers": (
                bookmaker_count
            ),

            "allowed_bookmakers": (
                allowed_bookmaker_count
            ),

            "total_odds": (
                odds_count
            ),

            "analysis_records": len(
                self.last_analysis_records
            ),

            "processed_at": (
                self.last_processed_at
            ),

        }

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return {

            "raw_events": deepcopy(
                self.last_raw_events
            ),

            "clean_events": deepcopy(
                self.last_clean_events
            ),

            "analysis_records": deepcopy(
                self.last_analysis_records
            ),

            "processed_at": (
                self.last_processed_at
            ),

            "summary": self.summary(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self,
    ) -> None:

        self.last_raw_events = []

        self.last_clean_events = []

        self.last_analysis_records = []

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

        if not isinstance(
            events,
            list,
        ):

            events = []

        self.last_raw_events = deepcopy(
            events
        )

        analysis_events = (
            self.prepare_for_analysis(
                events
            )
        )

        analysis_records = (
            self.last_analysis_records
        )

        return {

            "raw_events": deepcopy(
                events
            ),

            "clean_events": deepcopy(
                self.last_clean_events
            ),

            "analysis_events": deepcopy(
                analysis_events
            ),

            "analysis_records": deepcopy(
                analysis_records
            ),

            "summary": self.summary(
                self.last_clean_events
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
   
