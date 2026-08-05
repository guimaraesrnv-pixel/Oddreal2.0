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
    ) -> str:
        return str(value or "").strip().lower()

    def bookmaker_display_name(
        value: Any,
    ) -> str:
        return str(value or "").strip()


class DataManager:
    """
    Camada responsável pelo ciclo de vida dos dados.
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
        """
        Retorna timestamp UTC em formato ISO.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:
        """
        Converte valor para string com segurança.
        """

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
        """
        Converte valor para float.
        """

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
        """
        Garante retorno de lista.
        """

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
        """
        Obtém a chave original da bookmaker.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return ""

        return (
            DataManager._safe_string(
                bookmaker.get(
                    "key"
                )
            )
        )

    @staticmethod
    def _bookmaker_title(
        bookmaker: Dict[str, Any],
    ) -> str:
        """
        Obtém o nome de apresentação da bookmaker.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return ""

        title = (
            DataManager._safe_string(
                bookmaker.get(
                    "title"
                )
            )
        )

        if title:
            return title

        return (
            DataManager._safe_string(
                bookmaker.get(
                    "key"
                )
            )
        )

    @classmethod
    def _is_allowed_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> bool:
        """
        Verifica se a bookmaker está autorizada.

        A função é tolerante a diferentes formatos
        de ALLOWED_BOOKMAKERS.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return False

        key = cls._bookmaker_key(
            bookmaker
        )

        title = cls._bookmaker_title(
            bookmaker
        )

        normalized_key = (
            normalize_bookmaker_name(
                key
            )
        )

        normalized_title = (
            normalize_bookmaker_name(
                title
            )
        )

        if not ALLOWED_BOOKMAKERS:
            return True

        normalized_allowed = set()

        for allowed in ALLOWED_BOOKMAKERS:

            try:

                normalized_allowed.add(
                    normalize_bookmaker_name(
                        allowed
                    )
                )

            except Exception:

                continue

        if normalized_key in normalized_allowed:
            return True

        if normalized_title in normalized_allowed:
            return True

        return False

    @classmethod
    def _clean_market(
        cls,
        market: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Limpa um mercado individual.
        """

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

        cleaned_market["key"] = (
            market_key
        )

        cleaned_market["last_update"] = (
            cls._safe_string(
                market.get(
                    "last_update"
                )
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

            cleaned_outcome = (
                deepcopy(
                    outcome
                )
            )

            cleaned_outcome["name"] = (
                name
            )

            price = cls._safe_float(
                outcome.get(
                    "price"
                )
            )

            if price is not None:
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

    @classmethod
    def _clean_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Limpa uma bookmaker sem destruir sua estrutura original.
        """

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

        cleaned_bookmaker = deepcopy(
            bookmaker
        )

        cleaned_bookmaker[
            "key"
        ] = key

        cleaned_bookmaker[
            "title"
        ] = title

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

        cleaned_bookmaker[
            "_normalized_key"
        ] = normalize_bookmaker_name(
            key
        )

        cleaned_bookmaker[
            "_display_name"
        ] = bookmaker_display_name(
            title or key
        )

        cleaned_bookmaker[
            "_allowed"
        ] = cls._is_allowed_bookmaker(
            bookmaker
        )

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
        """
        Limpa bookmakers recebidos da API.

        IMPORTANTE:
        não elimina a bookmaker apenas porque ela não está
        autorizada.

        O campo `_allowed` informa o resultado do filtro.

        Isso evita que um problema de configuração em
        config/bookmakers.py transforme todos os eventos
        em eventos sem odds.
        """

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
        """
        Verifica estrutura mínima do evento.
        """

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
        Limpa e padroniza um evento.

        Os dados originais são preservados sempre que possível.
        """

        if not self.validate_event(
            event
        ):
            return None

        cleaned = deepcopy(
            event
        )

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

        # ======================================================
        # BOOKMAKERS
        # ======================================================

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

        cleaned_bookmakers = (
            self._clean_bookmakers(
                original_bookmakers
            )
        )

        cleaned[
            "bookmakers"
        ] = cleaned_bookmakers

        # ======================================================
        # CONTAGEM DE BOOKMAKERS
        # ======================================================

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
        """
        Limpa uma coleção de eventos.
        """

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
    # PREPARAÇÃO DE EVENTOS JÁ LIMPOS
    # ==========================================================

    def _prepare_clean_events(
        self,
        cleaned_events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Prepara eventos que já foram limpos.

        Evita executar clean_events() novamente.
        """

        if not isinstance(
            cleaned_events,
            list,
        ):
            return []

        prepared: List[
            Dict[str, Any]
        ] = []

        for event in cleaned_events:

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

            usable_bookmakers: List[
                Dict[str, Any]
            ] = []

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

                usable_markets = [
                    market
                    for market in markets
                    if (
                        isinstance(
                            market,
                            dict,
                        )
                        and isinstance(
                            market.get(
                                "outcomes"
                            ),
                            list,
                        )
                        and bool(
                            market.get(
                                "outcomes"
                            )
                        )
                    )
                ]

                if not usable_markets:
                    continue

                cleaned_bookmaker = deepcopy(
                    bookmaker
                )

                cleaned_bookmaker[
                    "markets"
                ] = usable_markets

                usable_bookmakers.append(
                    cleaned_bookmaker
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

        return prepared

    # ==========================================================
    # EXTRAÇÃO DE ODDS
    # ==========================================================

    def extract_odds_records(
        self,
        events: List[
            Dict[str, Any]
        ],
        allowed_only: bool = True,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Converte a estrutura da API em registros individuais
        de odds.

        Cada registro representa:

        evento
        bookmaker
        mercado
        outcome
        odd

        O cálculo quantitativo continua fora deste módulo.
        """

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

            bookmakers = (
                event.get(
                    "bookmakers",
                    [],
                )
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
                    True,
                )

                if (
                    allowed_only
                    and not allowed
                ):
                    continue

                bookmaker_key = (
                    self._safe_string(
                        bookmaker.get(
                            "key"
                        )
                    )
                )

                bookmaker_title = (
                    self._safe_string(
                        bookmaker.get(
                            "title"
                        ),
                        bookmaker_key,
                    )
                )

                markets = (
                    bookmaker.get(
                        "markets",
                        [],
                    )
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

                    outcomes = (
                        market.get(
                            "outcomes",
                            [],
                        )
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
        """
        Prepara eventos para o Pipeline.

        Um evento não é descartado apenas porque uma
        bookmaker não foi autorizada.

        O evento somente é descartado quando realmente
        não possui bookmakers/mercados utilizáveis.
        """

        cleaned_events = (
            self.clean_events(
                events
            )
        )

        prepared = (
            self._prepare_clean_events(
                cleaned_events
            )
        )

        records = (
            self.extract_odds_records(
                prepared,
                allowed_only=True,
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
        """
        Cria uma versão enxuta dos dados para a IA.
        """

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
        """
        Retorna resumo do conjunto atual.
        """

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

            if isinstance(
                bookmakers,
                list,
            ):

                bookmaker_count += len(
                    bookmakers
                )

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

            "total_odds": (
                odds_count
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
        """
        Retorna snapshot seguro do estado atual.
        """

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
        """
        Limpa estado temporário.
        """

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
        """
        Executa ciclo completo de gerenciamento.
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

        # ------------------------------------------------------
        # Limpeza única
        # ------------------------------------------------------

        clean_events = (
            self.clean_events(
                events
            )
        )

        # ------------------------------------------------------
        # Preparação sem limpar novamente
        # ------------------------------------------------------

        analysis_events = (
            self._prepare_clean_events(
                clean_events
            )
        )

        # ------------------------------------------------------
        # Registros individuais de odds
        # ------------------------------------------------------

        analysis_records = (
            self.extract_odds_records(
                analysis_events,
                allowed_only=True,
            )
        )

        info(
            "DataManager concluiu processamento: "
            f"{len(clean_events)} eventos limpos, "
            f"{len(analysis_events)} eventos preparados, "
            f"{len(analysis_records)} registros de odds."
        )

        return {

            "raw_events": deepcopy(
                events
            ),

            "clean_events": (
                clean_events
            ),

            "analysis_events": (
                analysis_events
            ),

            "analysis_records": (
                analysis_records
            ),

            "summary": self.summary(
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
