"""
OddReal 2.0
Gerenciador de Dados

Responsabilidades:
- receber dados da API;
- validar eventos;
- limpar estruturas inválidas;
- padronizar informações;
- preservar dados brutos;
- preservar TODOS os bookmakers recebidos;
- normalizar bookmakers;
- preparar eventos para análise;
- extrair registros de odds;
- preparar dados para IA;
- fornecer estatísticas básicas.

IMPORTANTE:

Este módulo NÃO decide quais bookmakers serão utilizados
pela análise.

O DataManager apenas:

1. recebe os dados;
2. valida a estrutura;
3. limpa dados inválidos;
4. preserva bookmakers recebidos;
5. preserva mercados válidos;
6. preserva outcomes válidos;
7. entrega tudo ao Analyzer/OddsEngine.

A decisão de quais bookmakers utilizar pertence à camada
de análise.

NÃO existe dependência de brokermaker neste módulo.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from modules.logger import info, warning, error


class DataManager:
    """
    Gerenciador central dos dados recebidos da API.

    O DataManager NÃO filtra bookmakers por uma lista
    pré-definida.

    Todos os bookmakers estruturalmente válidos recebidos
    da API permanecem disponíveis para as camadas superiores.
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
        Retorna o horário atual em UTC.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    # ----------------------------------------------------------
    # STRING
    # ----------------------------------------------------------

    @staticmethod
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:
        """
        Converte um valor para string com segurança.
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

    # ----------------------------------------------------------
    # FLOAT
    # ----------------------------------------------------------

    @staticmethod
    def _safe_float(
        value: Any,
        default: Optional[float] = None,
    ) -> Optional[float]:
        """
        Converte um valor para float.

        Valores NaN e infinitos são rejeitados.
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

    # ----------------------------------------------------------
    # LIST
    # ----------------------------------------------------------

    @staticmethod
    def _safe_list(
        value: Any,
    ) -> List[Any]:
        """
        Garante que o valor seja uma lista.
        """

        if isinstance(
            value,
            list,
        ):
            return value

        return []

    # ==========================================================
    # BOOKMAKER
    # ==========================================================

    @staticmethod
    def _bookmaker_key(
        bookmaker: Dict[str, Any],
    ) -> str:
        """
        Retorna a bookmaker key original enviada pela API.
        """

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

    # ----------------------------------------------------------

    @staticmethod
    def _bookmaker_title(
        bookmaker: Dict[str, Any],
    ) -> str:
        """
        Retorna o título da bookmaker.

        Se não existir title, utiliza key.
        """

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

    # ----------------------------------------------------------

    @classmethod
    def _normalized_bookmaker(
        cls,
        bookmaker: Dict[str, Any],
    ) -> Optional[str]:
        """
        Cria uma identificação normalizada da bookmaker.

        Não existe lista de bookmakers permitidos aqui.

        O objetivo é somente facilitar a identificação
        posterior pela camada de análise.
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

        # --------------------------------------------------
        # PRIMEIRA TENTATIVA: KEY
        # --------------------------------------------------

        if key:

            normalized = (
                key
                .strip()
                .lower()
            )

            if normalized:

                return normalized

        # --------------------------------------------------
        # SEGUNDA TENTATIVA: TITLE
        # --------------------------------------------------

        if title:

            normalized = (
                title
                .strip()
                .lower()
            )

            if normalized:

                return normalized

        return None

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
        """
        Limpa um mercado.

        Somente mercados estruturalmente inválidos são
        descartados.

        Nenhuma bookmaker é filtrada aqui.
        """

        if not isinstance(
            market,
            dict,
        ):
            return None

        # ------------------------------------------------------
        # MARKET KEY
        # ------------------------------------------------------

        market_key = cls._safe_string(
            market.get(
                "key"
            )
        )

        if not market_key:

            warning(
                "Mercado descartado: "
                "market key ausente."
            )

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

        # ------------------------------------------------------
        # OUTCOMES
        # ------------------------------------------------------

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

            outcome_name = cls._safe_string(
                outcome.get(
                    "name"
                )
            )

            if not outcome_name:

                warning(
                    "Outcome descartado: "
                    "nome ausente."
                )

                continue

            price = cls._safe_float(
                outcome.get(
                    "price"
                )
            )

            # --------------------------------------------------
            # ODDS
            # --------------------------------------------------

            if (
                price is None
                or price <= 1.0
            ):

                warning(
                    "Outcome descartado: "
                    f"odd inválida "
                    f"({outcome.get('price')!r})."
                )

                continue

            cleaned_outcome = deepcopy(
                outcome
            )

            cleaned_outcome[
                "name"
            ] = outcome_name

            cleaned_outcome[
                "price"
            ] = price

            # --------------------------------------------------
            # POINT
            # --------------------------------------------------

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

        # ------------------------------------------------------
        # NENHUM OUTCOME VÁLIDO
        # ------------------------------------------------------

        if not cleaned_outcomes:

            warning(
                "Mercado "
                f"'{market_key}' descartado: "
                "nenhum outcome válido."
            )

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
        """
        Limpa uma bookmaker.

        IMPORTANTE:

        Nenhuma bookmaker é eliminada por nome.

        Se a API enviou a bookmaker e ela possui mercados
        válidos, ela permanece disponível.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return None

        # ------------------------------------------------------
        # IDENTIFICAÇÃO
        # ------------------------------------------------------

        key = cls._bookmaker_key(
            bookmaker
        )

        title = cls._bookmaker_title(
            bookmaker
        )

        if not key and not title:

            warning(
                "Bookmaker descartada: "
                "key e title ausentes."
            )

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

        # ------------------------------------------------------
        # IDENTIFICAÇÃO NORMALIZADA
        # ------------------------------------------------------

        cleaned_bookmaker[
            "_normalized_key"
        ] = normalized

        cleaned_bookmaker[
            "_display_name"
        ] = (
            title
            or key
            or normalized
            or "Bookmaker"
        )

        # ------------------------------------------------------
        # IMPORTANTE
        # ------------------------------------------------------
        #
        # Não existe mais:
        #
        # ALLOWED_BOOKMAKERS
        #
        # Não existe:
        #
        # bookmaker_allowed
        #
        # Não existe:
        #
        # filtro por bookmaker.
        #
        # A API entregou -> permanece disponível.
        # ------------------------------------------------------

        cleaned_bookmaker[
            "_allowed"
        ] = True

        # ------------------------------------------------------
        # MARKETS
        # ------------------------------------------------------

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

            try:

                cleaned_market = (
                    cls._clean_market(
                        market
                    )
                )

                if cleaned_market is not None:

                    cleaned_markets.append(
                        cleaned_market
                    )

            except Exception as exc:

                error(
                    "Erro ao limpar mercado "
                    f"da bookmaker '{key}': "
                    f"{exc}"
                )

        cleaned_bookmaker[
            "markets"
        ] = cleaned_markets

        # ------------------------------------------------------
        # BOOKMAKER SEM MERCADOS
        # ------------------------------------------------------

        if not cleaned_markets:

            warning(
                f"Bookmaker '{key or title}' "
                "não possui mercados válidos."
            )

            return None

        return cleaned_bookmaker

    # ----------------------------------------------------------

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
        Limpa todas as bookmakers recebidas.

        Não existe filtro de bookmakers autorizadas.
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
    # VALIDAÇÃO DE EVENTO
    # ==========================================================

    def validate_event(
        self,
        event: Dict[str, Any],
    ) -> bool:
        """
        Verifica se o evento possui os campos mínimos.
        """

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

            warning(
                "Evento inválido: ID ausente."
            )

            return False

        if not home_team:

            warning(
                f"Evento {event_id}: "
                "home_team ausente."
            )

            return False

        if not away_team:

            warning(
                f"Evento {event_id}: "
                "away_team ausente."
            )

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
        """

        if not self.validate_event(
            event
        ):
            return None

        cleaned = deepcopy(
            event
        )

        # ------------------------------------------------------
        # IDENTIFICAÇÃO
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # BOOKMAKERS ORIGINAIS
        # ------------------------------------------------------

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
            "bookmakers da API."
        )

        # ------------------------------------------------------
        # LIMPEZA
        # ------------------------------------------------------

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

        # Como não existe mais uma lista de bookmakers
        # permitidas, todas as bookmakers preservadas são
        # consideradas disponíveis para análise.

        cleaned[
            "_allowed_bookmaker_count"
        ] = len(
            cleaned_bookmakers
        )

        cleaned[
            "_processed_at"
        ] = self._now_iso()

        info(
            f"Evento "
            f"{cleaned['home_team']} x "
            f"{cleaned['away_team']} ficou com "
            f"{len(cleaned_bookmakers)} "
            "bookmakers após limpeza."
        )

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
        Limpa uma lista de eventos.
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

        self.last_clean_events = deepcopy(
            cleaned_events
        )

        self.last_processed_at = (
            self._now_iso()
        )

        info(
            "DataManager preservou "
            f"{len(cleaned_events)} eventos."
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
        """
        Extrai cada odd individualmente.

        O parâmetro allowed_only permanece apenas para
        compatibilidade com chamadas antigas.

        Porém, neste DataManager, todas as bookmakers
        preservadas são consideradas disponíveis.
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

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):
                continue

            # --------------------------------------------------
            # BOOKMAKERS
            # --------------------------------------------------

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                # --------------------------------------------------
                # NÃO FILTRAR BOOKMAKER
                # --------------------------------------------------
                #
                # O parâmetro allowed_only é mantido para
                # compatibilidade, mas a nova arquitetura não
                # possui uma lista externa de bookmakers permitidas.
                #
                # Portanto, se a bookmaker chegou até aqui,
                # ela pode ser analisada.
                # --------------------------------------------------

                bookmaker_key = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or self._safe_string(
                        bookmaker.get(
                            "key"
                        )
                    ).lower()
                    or self._safe_string(
                        bookmaker.get(
                            "title"
                        )
                    ).lower()
                )

                if not bookmaker_key:

                    continue

                bookmaker_title = (
                    bookmaker.get(
                        "_display_name"
                    )
                    or bookmaker.get(
                        "title"
                    )
                    or bookmaker.get(
                        "key"
                    )
                    or bookmaker_key
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

                # --------------------------------------------------
                # MERCADOS
                # --------------------------------------------------

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

                    # --------------------------------------------------
                    # OUTCOMES
                    # --------------------------------------------------

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

                        if not outcome_name:

                            continue

                        if (
                            odd is None
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

                            # Mantido por compatibilidade.
                            # Agora sempre representa uma
                            # bookmaker preservada pelo fluxo.
                            "bookmaker_allowed": True,

                            "market_key": (
                                market_key
                            ),

                            "outcome_name": (
                                outcome_name
                            ),

                            "odd": odd,
                        }

                        # --------------------------------------------------
                        # POINT
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
        Prepara os eventos para o Analyzer.

        Nenhuma bookmaker é removida por nome.
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

                # --------------------------------------------------
                # NÃO FILTRAR POR BOOKMAKER
                # --------------------------------------------------

                if markets:

                    usable_bookmakers.append(
                        bookmaker
                    )

            # --------------------------------------------------
            # EVENTO SEM BOOKMAKERS
            # --------------------------------------------------

            if not usable_bookmakers:

                warning(
                    "Evento "
                    f"{event.get('id')} "
                    "não possui bookmakers com "
                    "mercados utilizáveis."
                )

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

        # ------------------------------------------------------
        # EXTRAÇÃO
        # ------------------------------------------------------

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
        Prepara resultados da análise para a IA.
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

                    "bookmaker_key": analysis.get(
                        "bookmaker_key"
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
        Retorna um resumo dos dados processados.
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
        allowed_bookmaker_count = 0
        odds_count = 0

        bookmaker_keys = set()

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

                key = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or bookmaker.get(
                        "key"
                    )
                )

                if key:

                    bookmaker_keys.add(
                        str(key)
                    )

                # Todas as bookmakers preservadas são
                # consideradas disponíveis.

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

            "unique_bookmakers": len(
                bookmaker_keys
            ),

            "bookmakers": sorted(
                bookmaker_keys
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
        """
        Retorna uma cópia do estado atual do DataManager.
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
        Limpa todo o estado armazenado.
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
        Executa o ciclo completo:

        API
        ↓
        dados brutos
        ↓
        limpeza
        ↓
        preparação
        ↓
        registros de odds
        ↓
        Analyzer
        """

        if not isinstance(
            events,
            list,
        ):

            events = []

        # ------------------------------------------------------
        # PRESERVAR DADOS BRUTOS
        # ------------------------------------------------------

        self.last_raw_events = deepcopy(
            events
        )

        info(
            "DataManager recebeu "
            f"{len(events)} eventos brutos."
        )

        # ------------------------------------------------------
        # PREPARAR
        # ------------------------------------------------------

        analysis_events = (
            self.prepare_for_analysis(
                events
            )
        )

        # ------------------------------------------------------
        # REGISTROS
        # ------------------------------------------------------

        analysis_records = (
            self.last_analysis_records
        )

        # ------------------------------------------------------
        # LOG FINAL
        # ------------------------------------------------------

        info(
            "DataManager processado: "
            f"{len(events)} eventos brutos, "
            f"{len(analysis_events)} eventos "
            "preparados e "
            f"{len(analysis_records)} "
            "registros de odds."
        )

        # ------------------------------------------------------
        # DIAGNÓSTICO DE BOOKMAKERS
        # ------------------------------------------------------

        unique_bookmakers = set()

        for event in analysis_events:

            for bookmaker in event.get(
                "bookmakers",
                [],
            ):

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                key = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or bookmaker.get(
                        "key"
                    )
                )

                if key:

                    unique_bookmakers.add(
                        str(key)
                    )

        info(
            "Bookmakers disponíveis após "
            "DataManager: "
            f"{sorted(unique_bookmakers)}"
        )

        info(
            "Total de bookmakers únicas após "
            "DataManager: "
            f"{len(unique_bookmakers)}"
        )

        # ------------------------------------------------------
        # RETORNO
        # ------------------------------------------------------

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


# ==========================================================
# EXPORTAÇÃO
# ==========================================================

__all__ = [
    "DataManager",
    "data_manager",
]
     
