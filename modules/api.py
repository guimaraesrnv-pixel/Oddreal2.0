"""
OddReal 2.0
Módulo de comunicação com The Odds API.

Responsabilidades:

- Comunicação com a The Odds API.
- Consulta de esportes e eventos.
- Consulta de odds.
- Registro das bookmakers reais retornadas pela API.
- Normalização das bookmakers através de bookmakers.py.
- Identificação das bookmakers autorizadas.
- Preparação dos dados para o DataManager.

IMPORTANTE
----------
Este módulo NÃO decide quais casas devem ser analisadas
por conta própria.

A whitelist oficial fica em:

    config.bookmakers.py

ou, dependendo da estrutura do projeto:

    config/bookmakers.py

O módulo apenas consulta essa configuração e marca cada
bookmaker com:

    _normalized_key
    _allowed
    _display_name
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from config.settings import Settings
from modules.cache_manager import cache
from modules.logger import info, warning, error

# ==========================================================
# WHITELIST DE BOOKMAKERS
# ==========================================================

try:
    from config.bookmakers import (
        normalize_bookmaker_name,
        is_allowed_bookmaker,
        bookmaker_display_name,
    )
except ImportError:
    try:
        from bookmakers import (
            normalize_bookmaker_name,
            is_allowed_bookmaker,
            bookmaker_display_name,
        )
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar bookmakers.py. "
            "Verifique se o arquivo está em config/bookmakers.py."
        ) from exc


# ==========================================================
# CLIENTE THE ODDS API
# ==========================================================

class OddsAPI:

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self) -> None:

        self.api_key = Settings.API_KEY
        self.timeout = 20

        info(
            "OddsAPIClient OddReal 2.0 inicializado."
        )

    # ======================================================
    # REQUEST
    # ======================================================

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Executa uma requisição para a The Odds API.

        Retorna:
            Dados JSON retornados pela API.

        Em caso de erro:
            {}.
        """

        if params is None:
            params = {}

        params = dict(params)

        params["apiKey"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        try:

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            info(
                "The Odds API respondeu com HTTP %s.",
                response.status_code,
            )

            return response.json()

        except requests.exceptions.Timeout:

            error(
                "Timeout ao acessar The Odds API."
            )

            return {}

        except requests.exceptions.HTTPError as exc:

            status_code = getattr(
                response,
                "status_code",
                "desconhecido",
            )

            error(
                "Erro HTTP %s na The Odds API: %s",
                status_code,
                exc,
            )

            return {}

        except requests.exceptions.RequestException as exc:

            error(
                "Erro de comunicação com The Odds API: %s",
                exc,
            )

            return {}

        except ValueError as exc:

            error(
                "The Odds API retornou JSON inválido: %s",
                exc,
            )

            return {}

        except Exception as exc:

            error(
                "Erro inesperado ao acessar The Odds API: %s",
                exc,
            )

            return {}

    # ======================================================
    # BOOKMAKER
    # ======================================================

    @staticmethod
    def _prepare_bookmaker(
        bookmaker: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Prepara uma bookmaker individual.

        A API normalmente retorna algo semelhante a:

        {
            "key": "bet365",
            "title": "bet365",
            "last_update": "...",
            "markets": [...]
        }

        O método adiciona:

            _normalized_key
            _allowed
            _display_name

        Sem alterar os campos originais da API.
        """

        if not isinstance(bookmaker, dict):

            warning(
                "Bookmaker ignorado porque não é um objeto JSON válido: %r",
                bookmaker,
            )

            return None

        prepared = dict(bookmaker)

        # --------------------------------------------------
        # KEY REAL DA API
        # --------------------------------------------------

        raw_key = prepared.get("key")

        raw_title = prepared.get("title")

        if raw_key is None:
            raw_key = ""

        if raw_title is None:
            raw_title = ""

        raw_key = str(raw_key).strip()

        raw_title = str(raw_title).strip()

        # --------------------------------------------------
        # LOG DA KEY REAL
        # --------------------------------------------------

        info(
            "Bookmaker recebido da API: key='%s' | title='%s'",
            raw_key,
            raw_title,
        )

        # --------------------------------------------------
        # NORMALIZAÇÃO
        # --------------------------------------------------

        normalized_key = normalize_bookmaker_name(
            raw_key
        )

        # --------------------------------------------------
        # FALLBACK PELO TITLE
        # --------------------------------------------------
        #
        # Algumas fontes podem possuir uma key que não
        # esteja cadastrada, mas um title reconhecível.
        #
        # Primeiro tentamos a key.
        # Se não funcionar, tentamos o title.
        #

        if normalized_key is None and raw_title:

            normalized_key = normalize_bookmaker_name(
                raw_title
            )

            if normalized_key is not None:

                info(
                    "Bookmaker reconhecido pelo title: "
                    "key='%s' | title='%s' | normalized='%s'",
                    raw_key,
                    raw_title,
                    normalized_key,
                )

        # --------------------------------------------------
        # AUTORIZAÇÃO
        # --------------------------------------------------

        allowed = False

        if normalized_key is not None:

            allowed = is_allowed_bookmaker(
                normalized_key
            )

        # --------------------------------------------------
        # NOME DE EXIBIÇÃO
        # --------------------------------------------------

        if normalized_key is not None:

            display_name = bookmaker_display_name(
                normalized_key
            )

        else:

            display_name = (
                raw_title
                or raw_key
                or "Casa não identificada"
            )

        # --------------------------------------------------
        # METADADOS INTERNOS
        # --------------------------------------------------

        prepared["_normalized_key"] = normalized_key

        prepared["_allowed"] = allowed

        prepared["_display_name"] = display_name

        prepared["_raw_key"] = raw_key

        # --------------------------------------------------
        # LOG FINAL
        # --------------------------------------------------

        if allowed:

            info(
                "BOOKMAKER AUTORIZADA: "
                "key='%s' | normalized='%s' | display='%s'",
                raw_key,
                normalized_key,
                display_name,
            )

        else:

            info(
                "BOOKMAKER NÃO AUTORIZADA: "
                "key='%s' | title='%s' | normalized='%s'",
                raw_key,
                raw_title,
                normalized_key,
            )

        return prepared

    # ======================================================
    # EVENTO
    # ======================================================

    def _prepare_event(
        self,
        event: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Prepara um evento retornado pela API.

        As bookmakers são analisadas e recebem os metadados
        internos utilizados posteriormente pelo DataManager.
        """

        if not isinstance(event, dict):

            warning(
                "Evento ignorado porque não é um objeto válido."
            )

            return None

        prepared_event = dict(event)

        bookmakers = prepared_event.get(
            "bookmakers",
            [],
        )

        if not isinstance(bookmakers, list):

            warning(
                "Evento %s possui bookmakers em formato inválido.",
                prepared_event.get("id"),
            )

            bookmakers = []

        prepared_bookmakers: List[Dict[str, Any]] = []

        for bookmaker in bookmakers:

            prepared = self._prepare_bookmaker(
                bookmaker
            )

            if prepared is not None:

                prepared_bookmakers.append(
                    prepared
                )

        prepared_event["bookmakers"] = (
            prepared_bookmakers
        )

        return prepared_event

    # ======================================================
    # EVENTOS
    # ======================================================

    def _prepare_events(
        self,
        data: Any,
    ) -> List[Dict[str, Any]]:
        """
        Prepara todos os eventos retornados pela API.
        """

        if not isinstance(data, list):

            warning(
                "Resposta de eventos não é uma lista."
            )

            return []

        prepared_events: List[Dict[str, Any]] = []

        for event in data:

            prepared = self._prepare_event(
                event
            )

            if prepared is not None:

                prepared_events.append(
                    prepared
                )

        return prepared_events

    # ======================================================
    # ESPORTES
    # ======================================================

    def get_sports(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Retorna a lista de esportes disponíveis.
        """

        cache_key = "sports"

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                "Sports carregados do cache."
            )

            return cached

        info(
            "Consultando lista de esportes."
        )

        sports = self._request(
            "sports"
        )

        if not isinstance(
            sports,
            list,
        ):

            warning(
                "A The Odds API não retornou uma lista de esportes."
            )

            return []

        cache.set(
            cache_key,
            sports,
            ttl=3600,
        )

        info(
            "%s esportes recebidos da The Odds API.",
            len(sports),
        )

        return sports

    # ======================================================
    # EVENTOS + ODDS
    # ======================================================

    def get_events(
        self,
        sport: str,
    ) -> List[Dict[str, Any]]:
        """
        Busca eventos e odds da The Odds API.

        Os bookmakers são preparados antes de serem
        entregues ao DataManager.
        """

        if not sport:

            warning(
                "get_events recebeu sport vazio."
            )

            return []

        cache_key = (
            f"events_{sport}"
        )

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                "Eventos do esporte '%s' carregados do cache.",
                sport,
            )

            return cached

        endpoint = (
            f"sports/{sport}/odds"
        )

        params = {
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
        }

        info(
            "Consultando odds: sport='%s' | endpoint='%s'",
            sport,
            endpoint,
        )

        data = self._request(
            endpoint,
            params,
        )

        prepared_events = (
            self._prepare_events(
                data
            )
        )

        # --------------------------------------------------
        # ESTATÍSTICAS DOS BOOKMAKERS
        # --------------------------------------------------

        total_bookmakers = 0
        allowed_bookmakers = 0
        rejected_bookmakers = 0

        for event in prepared_events:

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            total_bookmakers += len(
                bookmakers
            )

            for bookmaker in bookmakers:

                if bookmaker.get(
                    "_allowed",
                    False,
                ):

                    allowed_bookmakers += 1

                else:

                    rejected_bookmakers += 1

            home = event.get(
                "home_team",
                "?",
            )

            away = event.get(
                "away_team",
                "?",
            )

            info(
                "Evento %s x %s recebeu %s bookmakers da API.",
                home,
                away,
                len(bookmakers),
            )

        info(
            "Resumo bookmakers: "
            "%s recebidas | %s autorizadas | %s não autorizadas.",
            total_bookmakers,
            allowed_bookmakers,
            rejected_bookmakers,
        )

        # --------------------------------------------------
        # CACHE
        # --------------------------------------------------

        cache.set(
            cache_key,
            prepared_events,
            ttl=120,
        )

        info(
            "%s eventos preparados para o DataManager.",
            len(prepared_events),
        )

        return prepared_events

    # ======================================================
    # ODDS DE EVENTO ESPECÍFICO
    # ======================================================

    def get_event_odds(
        self,
        sport: str,
        event_id: str,
    ) -> Dict[str, Any]:
        """
        Busca odds de um evento específico.

        As bookmakers também passam pela mesma normalização
        utilizada em get_events().
        """

        if not sport:

            warning(
                "get_event_odds recebeu sport vazio."
            )

            return {}

        if not event_id:

            warning(
                "get_event_odds recebeu event_id vazio."
            )

            return {}

        endpoint = (
            f"sports/{sport}/events/"
            f"{event_id}/odds"
        )

        params = {
            "regions": "eu",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "decimal",
        }

        info(
            "Consultando odds do evento: "
            "sport='%s' | event_id='%s'",
            sport,
            event_id,
        )

        data = self._request(
            endpoint,
            params,
        )

        if not isinstance(
            data,
            dict,
        ):

            warning(
                "Resposta de odds do evento %s não é um objeto válido.",
                event_id,
            )

            return {}

        prepared = self._prepare_event(
            data
        )

        if prepared is None:

            return {}

        return prepared

    # ======================================================
    # DIAGNÓSTICO DAS BOOKMAKERS
    # ======================================================

    def get_events_diagnostic(
        self,
        sport: str,
    ) -> List[Dict[str, Any]]:
        """
        Método auxiliar de diagnóstico.

        Executa a consulta normalmente, mas deixa os dados
        preparados com todas as informações necessárias
        para verificar quais bookmakers a API realmente
        está enviando.

        Não altera a lógica principal do sistema.
        """

        info(
            "Iniciando diagnóstico de bookmakers "
            "para sport='%s'.",
            sport,
        )

        events = self.get_events(
            sport
        )

        for event in events:

            home = event.get(
                "home_team",
                "?",
            )

            away = event.get(
                "away_team",
                "?",
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            info(
                "DIAGNÓSTICO | %s x %s | bookmakers=%s",
                home,
                away,
                len(bookmakers),
            )

            for bookmaker in bookmakers:

                info(
                    "DIAGNÓSTICO BOOKMAKER | "
                    "key='%s' | title='%s' | "
                    "normalized='%s' | allowed=%s",
                    bookmaker.get(
                        "_raw_key"
                    ),
                    bookmaker.get(
                        "title"
                    ),
                    bookmaker.get(
                        "_normalized_key"
                    ),
                    bookmaker.get(
                        "_allowed",
                        False,
                    ),
                )

        return events


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

api = OddsAPI()


__all__ = [
    "OddsAPI",
    "api",
]
