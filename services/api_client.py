"""
OddReal 2.0
Cliente da The Odds API

Responsável por:

- Comunicação com a The Odds API;
- Requisições HTTP;
- Tratamento de erros;
- Controle básico de cache;
- Registro de consumo da API;
- Retorno padronizado dos eventos.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests

from config.settings import (
    API_KEY,
    BASE_URL,
    SPORT,
    REGIONS,
    MARKETS,
    ODDS_FORMAT,
)

from modules.logger import info, error


class OddsAPIClient:
    """
    Cliente central da The Odds API.
    """

    def __init__(
        self,
        timeout: int = 30,
        cache_seconds: int = 60,
    ) -> None:

        self.timeout = timeout

        self.cache_seconds = (
            cache_seconds
        )

        self.session = requests.Session()

        self._cached_events: Optional[
            List[Dict[str, Any]]
        ] = None

        self._cache_timestamp = 0.0

        self.last_response_info: Dict[
            str, Any
        ] = {}

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    def _request_params(
        self,
    ) -> Dict[str, Any]:
        """
        Monta os parâmetros da requisição.
        """

        return {

            "apiKey": API_KEY,

            "regions": REGIONS,

            "markets": MARKETS,

            "oddsFormat": ODDS_FORMAT,

        }

    # ==========================================================
    # CACHE
    # ==========================================================

    def _cache_is_valid(
        self,
    ) -> bool:
        """
        Verifica se o cache ainda está válido.
        """

        if self._cached_events is None:

            return False

        elapsed = (
            time.time()
            - self._cache_timestamp
        )

        return elapsed < self.cache_seconds

    def clear_cache(
        self,
    ) -> None:
        """
        Limpa o cache local.
        """

        self._cached_events = None

        self._cache_timestamp = 0.0

    # ==========================================================
    # REQUISIÇÃO
    # ==========================================================

    def _request(
        self,
    ) -> Optional[
        requests.Response
    ]:
        """
        Executa a requisição HTTP.
        """

        url = (
            f"{BASE_URL}/"
            f"{SPORT}/odds"
        )

        try:

            response = self.session.get(

                url,

                params=self._request_params(),

                timeout=self.timeout,

            )

            self.last_response_info = {

                "status_code": (
                    response.status_code
                ),

                "remaining_requests": (
                    response.headers.get(
                        "x-requests-remaining"
                    )
                ),

                "used_requests": (
                    response.headers.get(
                        "x-requests-used"
                    )
                ),

            }

            response.raise_for_status()

            return response

        except requests.Timeout:

            error(
                "The Odds API excedeu "
                "o tempo limite."
            )

            return None

        except requests.HTTPError as exc:

            status = (
                exc.response.status_code
                if exc.response is not None
                else "desconhecido"
            )

            error(
                "Erro HTTP na The Odds API: "
                f"{status}"
            )

            return None

        except requests.RequestException as exc:

            error(
                "Erro de comunicação com "
                f"a The Odds API: {exc}"
            )

            return None

        except Exception as exc:

            error(
                "Erro inesperado na API: "
                f"{exc}"
            )

            return None

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def get_events(
        self,
        force_refresh: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Busca eventos e odds na The Odds API.

        Se o cache estiver válido, evita uma nova
        requisição desnecessária.
        """

        if (
            not force_refresh
            and self._cache_is_valid()
        ):

            info(
                "Eventos carregados "
                "a partir do cache."
            )

            return list(
                self._cached_events or []
            )

        response = self._request()

        if response is None:

            # Se a API falhar mas houver dados antigos,
            # mantemos o último resultado disponível.

            if self._cached_events:

                info(
                    "API indisponível. "
                    "Utilizando último cache válido."
                )

                return list(
                    self._cached_events
                )

            return []

        try:

            data = response.json()

        except ValueError:

            error(
                "A The Odds API retornou "
                "uma resposta JSON inválida."
            )

            return []

        if not isinstance(
            data,
            list,
        ):

            error(
                "Formato inesperado retornado "
                "pela The Odds API."
            )

            return []

        events = [

            item

            for item in data

            if isinstance(
                item,
                dict,
            )

        ]

        self._cached_events = list(
            events
        )

        self._cache_timestamp = (
            time.time()
        )

        info(
            "The Odds API retornou "
            f"{len(events)} eventos."
        )

        return events

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(
        self,
    ) -> bool:
        """
        Verifica se a API está respondendo.
        """

        response = self._request()

        return response is not None

    # ==========================================================
    # INFORMAÇÕES DA API
    # ==========================================================

    def api_status(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna informações básicas da última requisição.
        """

        return {

            "status_code": (
                self.last_response_info.get(
                    "status_code"
                )
            ),

            "remaining_requests": (
                self.last_response_info.get(
                    "remaining_requests"
                )
            ),

            "used_requests": (
                self.last_response_info.get(
                    "used_requests"
                )
            ),

            "cached": (
                self._cache_is_valid()
            ),

        }


api_client = OddsAPIClient()
