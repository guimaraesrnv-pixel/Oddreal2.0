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

from config.settings import settings

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

    def _get_setting(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Obtém uma configuração da instância
        global de Settings.

        Aceita tanto atributos diretos
        quanto propriedades/configurações
        agrupadas.
        """

        try:

            value = getattr(
                settings,
                name,
                default,
            )

            if value is None:
                return default

            return value

        except Exception as exc:

            error(
                f"Erro ao obter configuração "
                f"'{name}': {exc}"
            )

            return default

    @property
    def api_key(self) -> str:
        """
        Retorna a chave da API.
        """

        return str(
            self._get_setting(
                "api_key",
                "",
            )
        )

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base da API.
        """

        return str(
            self._get_setting(
                "base_url",
                "https://api.the-odds-api.com/v4",
            )
        ).rstrip("/")

    @property
    def sport(self) -> str:
        """
        Retorna o esporte padrão.
        """

        return str(
            self._get_setting(
                "sport",
                "soccer",
            )
        )

    @property
    def regions(self) -> str:
        """
        Retorna as regiões das casas.
        """

        return str(
            self._get_setting(
                "regions",
                "us",
            )
        )

    @property
    def markets(self) -> str:
        """
        Retorna os mercados consultados.
        """

        return str(
            self._get_setting(
                "markets",
                "h2h",
            )
        )

    @property
    def odds_format(self) -> str:
        """
        Retorna o formato das odds.
        """

        return str(
            self._get_setting(
                "odds_format",
                "decimal",
            )
        )

    def _cache_valid(self) -> bool:
        """
        Verifica se o cache atual ainda é válido.
        """

        if self._cached_events is None:
            return False

        elapsed = (
            time.time()
            - self._cache_timestamp
        )

        return (
            elapsed
            < self.cache_seconds
        )

    def _build_url(
        self,
        endpoint: str,
    ) -> str:
        """
        Monta a URL completa da requisição.
        """

        endpoint = endpoint.lstrip("/")

        return (
            f"{self.base_url}/{endpoint}"
        )

    def _build_params(
        self,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        Monta os parâmetros padrão
        da The Odds API.
        """

        params: Dict[
            str, Any
        ] = {

            "apiKey": self.api_key,

            "regions": self.regions,

            "markets": self.markets,

            "oddsFormat": self.odds_format,
        }

        for key, value in extra_params.items():

            if value is not None:

                params[key] = value

        return params

    def _request(
        self,
        endpoint: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:
        """
        Executa uma requisição GET.
        """

        url = self._build_url(
            endpoint
        )

        try:

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            self.last_response_info = {

                "status_code":
                    response.status_code,

                "url":
                    response.url,

                "headers":
                    dict(response.headers),
            }

            response.raise_for_status()

            info(
                "The Odds API respondeu "
                f"com HTTP "
                f"{response.status_code}"
            )

            return response.json()

        except requests.exceptions.Timeout:

            error(
                "Timeout ao consultar "
                "a The Odds API."
            )

            return []

        except requests.exceptions.HTTPError as exc:

            error(
                "Erro HTTP na The Odds API: "
                f"{exc}"
            )

            return []

        except requests.exceptions.RequestException as exc:

            error(
                "Erro de conexão com "
                f"a The Odds API: {exc}"
            )

            return []

        except ValueError as exc:

            error(
                "Resposta JSON inválida "
                f"da The Odds API: {exc}"
            )

            return []

        except Exception as exc:

            error(
                "Erro inesperado ao consultar "
                f"a The Odds API: {exc}"
            )

            return []

    def get_events(
        self,
        sport: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Busca eventos esportivos.

        Utiliza cache para evitar chamadas
        desnecessárias à API.
        """

        if (
            not force_refresh
            and self._cache_valid()
        ):

            info(
                "Retornando eventos "
                "a partir do cache."
            )

            return (
                self._cached_events
                or []
            )

        selected_sport = (
            sport
            or self.sport
        )

        endpoint = (
            f"sports/"
            f"{selected_sport}/odds"
        )

        params = self._build_params()

        events = self._request(
            endpoint,
            params,
        )

        if not isinstance(
            events,
            list,
        ):

            events = []

        self._cached_events = events

        self._cache_timestamp = (
            time.time()
        )

        info(
            f"{len(events)} eventos "
            "recebidos da The Odds API."
        )

        return events

    def get_sports(
        self,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Retorna a lista de esportes disponíveis.
        """

        data = self._request(
            "sports",
            {
                "apiKey": self.api_key,
            },
        )

        if not isinstance(
            data,
            list,
        ):

            return []

        return data

    def clear_cache(
        self,
    ) -> None:
        """
        Limpa o cache de eventos.
        """

        self._cached_events = None

        self._cache_timestamp = 0.0

        info(
            "Cache da Odds API "
            "limpo."
        )

    def get_last_response_info(
        self,
    ) -> Dict[
        str, Any
    ]:
        """
        Retorna informações da última
        resposta HTTP.
        """

        return dict(
            self.last_response_info
        )

    def health_check(
        self,
    ) -> bool:
        """
        Verifica se a API está respondendo.
        """

        data = self.get_sports()

        return isinstance(
            data,
            list,
        )


api_client = OddsAPIClient()
