"""
OddReal 2.0
Comunicação com The Odds API

Responsabilidades:
- comunicação com The Odds API v4;
- autenticação;
- consulta de esportes;
- consulta de eventos;
- consulta de odds;
- utilização de cache;
- tratamento de erros;
- normalização básica da resposta;
- filtragem dos bookmakers autorizados pelo OddReal.

IMPORTANTE
----------
O API NÃO calcula:

- probabilidade;
- EV;
- Value Bet;
- Índice OddReal;
- consenso de mercado.

Essas responsabilidades permanecem no Analyzer/OddsEngine.

O filtro de bookmakers deste módulo serve apenas para garantir
que o restante do sistema receba as casas autorizadas na
configuração do OddReal.

A lista de bookmakers autorizados fica em:

    config/bookmakers.py
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

import requests

from config.settings import Settings
from config.bookmakers import (
    ALLOWED_BOOKMAKERS,
    normalize_bookmaker_name,
    bookmaker_display_name,
)

from modules.cache_manager import cache
from modules.logger import (
    info,
    warning,
    error,
)


class OddsAPI:
    """
    Cliente responsável pela comunicação com a The Odds API.
    """

    BASE_URL = (
        "https://api.the-odds-api.com/v4"
    )

    def __init__(self) -> None:

        self.api_key = Settings.API_KEY

        self.timeout = 20

        info(
            "OddsAPIClient OddReal 2.0 inicializado."
        )

    # ==========================================================
    # REQUISIÇÃO BASE
    # ==========================================================

    def _request(
        self,
        endpoint: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:
        """
        Executa uma requisição GET contra a The Odds API.

        Retorna:
            JSON da API em caso de sucesso.

        Retorna:
            {} em caso de erro.
        """

        if params is None:
            params = {}

        request_params = dict(
            params
        )

        request_params[
            "apiKey"
        ] = self.api_key

        url = (
            f"{self.BASE_URL}/"
            f"{endpoint}"
        )

        try:

            response = requests.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )

            info(
                "The Odds API respondeu "
                f"com HTTP "
                f"{response.status_code}."
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:

            error(
                "Timeout ao acessar "
                "The Odds API."
            )

            return {}

        except requests.exceptions.ConnectionError as exc:

            error(
                "Erro de conexão com "
                f"The Odds API: {exc}"
            )

            return {}

        except requests.exceptions.HTTPError as exc:

            status_code = None

            if exc.response is not None:
                status_code = (
                    exc.response.status_code
                )

            error(
                "Erro HTTP ao acessar "
                f"The Odds API "
                f"(status={status_code}): "
                f"{exc}"
            )

            return {}

        except ValueError as exc:

            error(
                "Resposta JSON inválida "
                f"da The Odds API: {exc}"
            )

            return {}

        except Exception as exc:

            error(
                "Erro inesperado ao acessar "
                f"The Odds API: {exc}"
            )

            return {}

    # ==========================================================
    # NORMALIZAÇÃO DE BOOKMAKERS
    # ==========================================================

    @staticmethod
    def _normalize_bookmaker(
        bookmaker: Any,
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Normaliza um bookmaker individual.

        O bookmaker somente é aceito quando
        pertence à lista branca definida em
        config.bookmakers.py.
        """

        if not isinstance(
            bookmaker,
            dict,
        ):
            return None

        key = str(
            bookmaker.get(
                "key",
                "",
            )
            or ""
        ).strip()

        title = str(
            bookmaker.get(
                "title",
                "",
            )
            or ""
        ).strip()

        # Tenta primeiro a key.
        normalized = (
            normalize_bookmaker_name(
                key
            )
        )

        # Se a key não for reconhecida,
        # tenta o title.
        if normalized is None:

            normalized = (
                normalize_bookmaker_name(
                    title
                )
            )

        # Casa desconhecida:
        # NÃO entra no pipeline.
        if normalized is None:

            return None

        # Segurança adicional.
        if normalized not in (
            ALLOWED_BOOKMAKERS
        ):

            return None

        cleaned = deepcopy(
            bookmaker
        )

        cleaned[
            "key"
        ] = key or normalized

        cleaned[
            "title"
        ] = bookmaker_display_name(
            normalized
        )

        cleaned[
            "_normalized_key"
        ] = normalized

        cleaned[
            "_display_name"
        ] = bookmaker_display_name(
            normalized
        )

        cleaned[
            "_allowed"
        ] = True

        return cleaned

    # ==========================================================
    # FILTRO DE BOOKMAKERS
    # ==========================================================

    @classmethod
    def _filter_bookmakers(
        cls,
        bookmakers: Any,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Mantém exclusivamente os bookmakers
        autorizados pelo OddReal.

        Bookmakers desconhecidos são descartados.
        """

        if not isinstance(
            bookmakers,
            list,
        ):
            return []

        filtered: List[
            Dict[str, Any]
        ] = []

        received = 0
        accepted = 0
        rejected = 0

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            received += 1

            normalized = (
                cls._normalize_bookmaker(
                    bookmaker
                )
            )

            if normalized is None:

                rejected += 1

                continue

            filtered.append(
                normalized
            )

            accepted += 1

        info(
            "Bookmakers filtrados: "
            f"{accepted} autorizados "
            f"de {received} recebidos."
        )

        if rejected:

            info(
                f"{rejected} bookmakers "
                "desconhecidos/não autorizados "
                "foram ignorados."
            )

        return filtered

    # ==========================================================
    # FILTRO DOS EVENTOS
    # ==========================================================

    @classmethod
    def _filter_events(
        cls,
        events: Any,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Filtra os bookmakers dentro de cada evento.

        Os eventos continuam existindo mesmo que
        nenhum bookmaker autorizado esteja disponível.

        Isso é importante para não destruir a resposta
        original da API nesta camada.
        """

        if not isinstance(
            events,
            list,
        ):
            return []

        filtered_events: List[
            Dict[str, Any]
        ] = []

        for event in events:

            if not isinstance(
                event,
                dict,
            ):
                continue

            cleaned_event = deepcopy(
                event
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            filtered_bookmakers = (
                cls._filter_bookmakers(
                    bookmakers
                )
            )

            cleaned_event[
                "bookmakers"
            ] = filtered_bookmakers

            cleaned_event[
                "_bookmaker_count"
            ] = len(
                filtered_bookmakers
            )

            filtered_events.append(
                cleaned_event
            )

        return filtered_events

    # ==========================================================
    # ESPORTES
    # ==========================================================

    def get_sports(
        self,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Retorna a lista de esportes disponíveis.
        """

        cache_key = (
            "oddreal_sports"
        )

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                "Sports carregados "
                "do cache."
            )

            return cached

        info(
            "Consultando lista "
            "de esportes."
        )

        sports = self._request(
            "sports"
        )

        if not isinstance(
            sports,
            list,
        ):

            warning(
                "The Odds API não retornou "
                "uma lista de esportes."
            )

            return []

        cache.set(
            cache_key,
            sports,
            ttl=3600,
        )

        return sports

    # ==========================================================
    # EVENTOS + ODDS
    # ==========================================================

    def get_events(
        self,
        sport: str,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Busca eventos e odds de um esporte.

        IMPORTANTE:
        A consulta utiliza a região us.

        O filtro final das casas não depende
        exclusivamente da região da API.

        O sistema consulta os bookmakers retornados
        e depois mantém somente os autorizados
        em config.bookmakers.py.
        """

        sport = str(
            sport or ""
        ).strip()

        if not sport:

            warning(
                "get_events recebeu "
                "sport vazio."
            )

            return []

        cache_key = (
            f"oddreal_events_{sport}"
        )

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                f"Eventos de {sport} "
                "carregados do cache."
            )

            return cached

        endpoint = (
            f"sports/{sport}/odds"
        )

        # ======================================================
        # ATENÇÃO
        # ======================================================
        #
        # Não usamos "eu" aqui.
        #
        # O objetivo do OddReal é trabalhar com as casas
        # autorizadas em config/bookmakers.py.
        #
        # A filtragem é feita depois da resposta da API.
        #
        # ======================================================

        params = {
            "regions": "us",
            "markets": "h2h",
            "oddsFormat": "decimal",
        }

        info(
            f"Consultando eventos de {sport} "
            "na The Odds API."
        )

        data = self._request(
            endpoint,
            params,
        )

        if not isinstance(
            data,
            list,
        ):

            warning(
                f"Nenhum evento válido "
                f"retornado para {sport}."
            )

            return []

        info(
            f"{len(data)} eventos "
            "recebidos da The Odds API."
        )

        filtered_data = (
            self._filter_events(
                data
            )
        )

        cache.set(
            cache_key,
            filtered_data,
            ttl=120,
        )

        return filtered_data

    # ==========================================================
    # ODDS DE EVENTO ESPECÍFICO
    # ==========================================================

    def get_event_odds(
        self,
        sport: str,
        event_id: str,
    ) -> Dict[str, Any]:
        """
        Busca odds detalhadas de um evento específico.

        Mantém somente bookmakers autorizados.
        """

        sport = str(
            sport or ""
        ).strip()

        event_id = str(
            event_id or ""
        ).strip()

        if not sport or not event_id:

            warning(
                "get_event_odds recebeu "
                "sport ou event_id vazio."
            )

            return {}

        endpoint = (
            f"sports/{sport}/events/"
            f"{event_id}/odds"
        )

        params = {
            "regions": "us",
            "markets": (
                "h2h,"
                "spreads,"
                "totals"
            ),
            "oddsFormat": "decimal",
        }

        data = self._request(
            endpoint,
            params,
        )

        if not isinstance(
            data,
            dict,
        ):

            return {}

        cleaned = deepcopy(
            data
        )

        bookmakers = data.get(
            "bookmakers",
            [],
        )

        cleaned[
            "bookmakers"
        ] = self._filter_bookmakers(
            bookmakers
        )

        cleaned[
            "_bookmaker_count"
        ] = len(
            cleaned[
                "bookmakers"
            ]
        )

        return cleaned

    # ==========================================================
    # ESTATÍSTICAS DE BOOKMAKERS
    # ==========================================================

    @staticmethod
    def bookmaker_summary(
        events: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Retorna um resumo dos bookmakers autorizados
        encontrados nos eventos.
        """

        counts: Dict[
            str,
            int
        ] = {}

        if not isinstance(
            events,
            list,
        ):
            return {
                "total": 0,
                "bookmakers": {},
            }

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

                normalized = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                )

                if not normalized:

                    normalized = (
                        normalize_bookmaker_name(
                            bookmaker.get(
                                "key",
                                bookmaker.get(
                                    "title",
                                    "",
                                ),
                            )
                        )
                    )

                if normalized is None:
                    continue

                if normalized not in (
                    ALLOWED_BOOKMAKERS
                ):
                    continue

                counts[
                    normalized
                ] = (
                    counts.get(
                        normalized,
                        0,
                    )
                    + 1
                )

        return {
            "total": sum(
                counts.values()
            ),
            "bookmakers": counts,
        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

api = OddsAPI()


__all__ = [
    "OddsAPI",
    "api",
]
