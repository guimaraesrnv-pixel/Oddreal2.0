"""
OddReal 2.0
Cliente da The Odds API

Responsável por:

- Comunicação com a The Odds API;
- Requisições HTTP;
- Tratamento de erros;
- Controle de cache;
- Controle básico de consumo;
- Validação da configuração;
- Retorno padronizado dos eventos;
- Health check da API.

A API Key nunca deve ser armazenada diretamente neste arquivo.
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
        timeout: Optional[int] = None,
        cache_seconds: int = 60,
    ) -> None:

        # ==========================================================
        # CONFIGURAÇÕES
        # ==========================================================

        # request_timeout pode não existir no Settings.
        # Nesse caso utilizamos 15 segundos como padrão seguro.
        configured_timeout = getattr(
            settings,
            "request_timeout",
            15,
        )

        try:
            configured_timeout = int(
                configured_timeout
            )
        except (
            TypeError,
            ValueError,
        ):
            configured_timeout = 15

        if configured_timeout <= 0:
            configured_timeout = 15

        self.timeout = (
            int(timeout)
            if timeout is not None
            else configured_timeout
        )

        if self.timeout <= 0:
            self.timeout = 15

        # Cache configurável sem depender de atributo
        # obrigatório no Settings.
        configured_cache = getattr(
            settings,
            "cache_seconds",
            cache_seconds,
        )

        try:
            configured_cache = int(
                configured_cache
            )
        except (
            TypeError,
            ValueError,
        ):
            configured_cache = cache_seconds

        self.cache_seconds = max(
            0,
            configured_cache,
        )

        # ==========================================================
        # SESSÃO HTTP
        # ==========================================================

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": "OddReal/2.0",
                "Accept": "application/json",
            }
        )

        # ==========================================================
        # CACHE
        # ==========================================================

        self._cached_events: Optional[
            List[Dict[str, Any]]
        ] = None

        self._cache_timestamp = 0.0

        # ==========================================================
        # INFORMAÇÕES DA ÚLTIMA RESPOSTA
        # ==========================================================

        self.last_response_info: Dict[
            str, Any
        ] = {}

        # ==========================================================
        # CONTROLE DE CONSUMO
        # ==========================================================

        self.remaining_requests: Optional[
            int
        ] = None

        self.used_requests: Optional[
            int
        ] = None

        self.last_error: Optional[
            str
        ] = None

        info(
            "OddsAPIClient OddReal 2.0 "
            "inicializado."
        )

    # ==========================================================
    # CONFIGURAÇÕES
    # ==========================================================

    @property
    def api_key(self) -> str:
        """
        Retorna a chave da The Odds API.

        A chave vem do Settings/Secrets.
        Nunca deve ser exibida em logs.
        """

        return str(
            getattr(
                settings,
                "api_key",
                "",
            )
            or ""
        ).strip()

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base da API.
        """

        return str(
            getattr(
                settings,
                "base_url",
                "https://api.the-odds-api.com/v4",
            )
            or "https://api.the-odds-api.com/v4"
        ).rstrip("/")

    @property
    def sport(self) -> str:
        """
        Esporte padrão.
        """

        return str(
            getattr(
                settings,
                "sport",
                "soccer",
            )
            or "soccer"
        ).strip()

    @property
    def regions(self) -> str:
        """
        Regiões das casas de apostas.
        """

        return str(
            getattr(
                settings,
                "regions",
                "us",
            )
            or "us"
        ).strip()

    @property
    def markets(self) -> str:
        """
        Mercados consultados.
        """

        return str(
            getattr(
                settings,
                "markets",
                "h2h",
            )
            or "h2h"
        ).strip()

    @property
    def odds_format(self) -> str:
        """
        Formato das odds.
        """

        return str(
            getattr(
                settings,
                "odds_format",
                "decimal",
            )
            or "decimal"
        ).strip()

    # ==========================================================
    # STATUS DA CONFIGURAÇÃO
    # ==========================================================

    def is_configured(self) -> bool:
        """
        Verifica se a API possui uma chave configurada.
        """

        return bool(
            self.api_key
        )

    # ==========================================================
    # CACHE
    # ==========================================================

    def _cache_valid(self) -> bool:
        """
        Verifica se o cache ainda é válido.
        """

        if self._cached_events is None:
            return False

        if self.cache_seconds <= 0:
            return False

        elapsed = (
            time.time()
            - self._cache_timestamp
        )

        return (
            elapsed
            < self.cache_seconds
        )

    def clear_cache(self) -> None:
        """
        Limpa o cache de eventos.
        """

        self._cached_events = None
        self._cache_timestamp = 0.0

        info(
            "Cache da The Odds API "
            "limpo."
        )

    # ==========================================================
    # URL
    # ==========================================================

    def _build_url(
        self,
        endpoint: str,
    ) -> str:
        """
        Monta a URL completa.
        """

        endpoint = (
            str(endpoint)
            .strip()
            .lstrip("/")
        )

        return (
            f"{self.base_url}/{endpoint}"
        )

    # ==========================================================
    # PARÂMETROS
    # ==========================================================

    def _build_params(
        self,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        Monta os parâmetros padrão.
        """

        params: Dict[
            str,
            Any
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

    # ==========================================================
    # REQUISIÇÃO HTTP
    # ==========================================================

    def _request(
        self,
        endpoint: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:
        """
        Executa uma requisição GET.

        A API Key nunca é registrada nos logs.
        """

        self.last_error = None

        # ------------------------------------------------------
        # VERIFICAÇÃO DA CHAVE
        # ------------------------------------------------------

        if not self.is_configured():

            message = (
                "The Odds API não configurada. "
                "A chave da API não foi encontrada "
                "nos Secrets/configuração."
            )

            self.last_error = message

            error(
                message
            )

            self.last_response_info = {
                "status_code": None,
                "url": self._build_url(
                    endpoint
                ),
                "error": (
                    "API key não configurada."
                ),
            }

            return []

        # ------------------------------------------------------
        # URL
        # ------------------------------------------------------

        url = self._build_url(
            endpoint
        )

        # ------------------------------------------------------
        # PARÂMETROS
        # ------------------------------------------------------

        request_params = (
            params
            if params is not None
            else self._build_params()
        )

        # ------------------------------------------------------
        # REQUEST
        # ------------------------------------------------------

        try:

            response = self.session.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )

            # --------------------------------------------------
            # CONSUMO DA API
            # --------------------------------------------------

            self._update_usage(
                response
            )

            # --------------------------------------------------
            # INFORMAÇÕES DA RESPOSTA
            # --------------------------------------------------

            self.last_response_info = {
                "status_code":
                    response.status_code,

                "url":
                    self._safe_response_url(
                        response
                    ),

                "remaining_requests":
                    self.remaining_requests,

                "used_requests":
                    self.used_requests,
            }

            # --------------------------------------------------
            # ERROS HTTP
            # --------------------------------------------------

            if response.status_code == 401:

                message = (
                    "The Odds API rejeitou "
                    "a chave de autenticação."
                )

                self.last_error = message

                error(
                    message
                )

                return []

            if response.status_code == 403:

                message = (
                    "Acesso negado pela "
                    "The Odds API."
                )

                self.last_error = message

                error(
                    message
                )

                return []

            if response.status_code == 429:

                message = (
                    "Limite de requisições da "
                    "The Odds API atingido."
                )

                self.last_error = message

                error(
                    message
                )

                return []

            response.raise_for_status()

            # --------------------------------------------------
            # JSON
            # --------------------------------------------------

            data = response.json()

            info(
                "The Odds API respondeu "
                f"com HTTP "
                f"{response.status_code}."
            )

            return data

        except requests.exceptions.Timeout:

            message = (
                "Timeout ao consultar "
                "a The Odds API."
            )

            self.last_error = message

            error(
                message
            )

            return []

        except requests.exceptions.ConnectionError:

            message = (
                "Erro de conexão com "
                "a The Odds API."
            )

            self.last_error = message

            error(
                message
            )

            return []

        except requests.exceptions.HTTPError as exc:

            message = (
                "Erro HTTP na "
                f"The Odds API: {exc}"
            )

            self.last_error = message

            error(
                message
            )

            return []

        except requests.exceptions.RequestException as exc:

            message = (
                "Erro de requisição na "
                f"The Odds API: {exc}"
            )

            self.last_error = message

            error(
                message
            )

            return []

        except ValueError as exc:

            message = (
                "Resposta JSON inválida "
                f"da The Odds API: {exc}"
            )

            self.last_error = message

            error(
                message
            )

            return []

        except Exception as exc:

            message = (
                "Erro inesperado ao consultar "
                f"a The Odds API: {exc}"
            )

            self.last_error = message

            error(
                message
            )

            return []

    # ==========================================================
    # CONSUMO DA API
    # ==========================================================

    def _update_usage(
        self,
        response: requests.Response,
    ) -> None:
        """
        Atualiza informações de consumo
        disponibilizadas pelos headers.
        """

        try:

            remaining = response.headers.get(
                "x-requests-remaining"
            )

            used = response.headers.get(
                "x-requests-used"
            )

            if remaining is not None:

                self.remaining_requests = int(
                    remaining
                )

            if used is not None:

                self.used_requests = int(
                    used
                )

        except (
            TypeError,
            ValueError,
        ):

            pass

    # ==========================================================
    # URL SEGURA PARA LOG/STATUS
    # ==========================================================

    @staticmethod
    def _safe_response_url(
        response: requests.Response,
    ) -> str:
        """
        Retorna a URL da resposta sem expor
        a API Key.
        """

        try:

            url = response.url

            if "apiKey=" in url:

                before, _ = url.split(
                    "apiKey=",
                    1,
                )

                return (
                    before
                    + "apiKey=***"
                )

            return url

        except Exception:

            return ""

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def get_events(
        self,
        sport: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Busca eventos esportivos.

        O retorno esperado é uma lista
        de eventos da The Odds API.
        """

        # ------------------------------------------------------
        # CACHE
        # ------------------------------------------------------

        if (
            not force_refresh
            and self._cache_valid()
        ):

            info(
                "Retornando eventos "
                "a partir do cache."
            )

            return list(
                self._cached_events
                or []
            )

        # ------------------------------------------------------
        # ESPORTE
        # ------------------------------------------------------

        selected_sport = (
            sport
            or self.sport
        )

        selected_sport = str(
            selected_sport
        ).strip()

        if not selected_sport:

            error(
                "Nenhum esporte "
                "foi configurado."
            )

            return []

        # ------------------------------------------------------
        # ENDPOINT
        # ------------------------------------------------------

        endpoint = (
            f"sports/"
            f"{selected_sport}/odds"
        )

        # ------------------------------------------------------
        # PARÂMETROS
        # ------------------------------------------------------

        params = self._build_params()

        # ------------------------------------------------------
        # CONSULTA
        # ------------------------------------------------------

        events = self._request(
            endpoint,
            params,
        )

        # ------------------------------------------------------
        # VALIDAÇÃO
        # ------------------------------------------------------

        if not isinstance(
            events,
            list,
        ):

            error(
                "A The Odds API retornou "
                "um formato inesperado "
                "para os eventos."
            )

            return []

        # ------------------------------------------------------
        # CACHE
        # ------------------------------------------------------

        self._cached_events = list(
            events
        )

        self._cache_timestamp = (
            time.time()
        )

        info(
            f"{len(events)} eventos "
            "recebidos da The Odds API."
        )

        return events

    # ==========================================================
    # ESPORTES
    # ==========================================================

    def get_sports(
        self,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Retorna esportes disponíveis.
        """

        data = self._request(
            "sports",
            {
                "apiKey":
                    self.api_key,
            },
        )

        if not isinstance(
            data,
            list,
        ):

            return []

        return data

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(
        self,
    ) -> bool:
        """
        Verifica se a API está configurada
        e respondendo.
        """

        if not self.is_configured():

            return False

        data = self.get_sports()

        return isinstance(
            data,
            list,
        )

    # ==========================================================
    # INFORMAÇÕES DA ÚLTIMA RESPOSTA
    # ==========================================================

    def get_last_response_info(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Retorna informações da última requisição.
        """

        return dict(
            self.last_response_info
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Retorna status do cliente.
        """

        return {
            "service":
                "The Odds API",

            "configured":
                self.is_configured(),

            "base_url":
                self.base_url,

            "sport":
                self.sport,

            "regions":
                self.regions,

            "markets":
                self.markets,

            "odds_format":
                self.odds_format,

            "timeout":
                self.timeout,

            "cache_seconds":
                self.cache_seconds,

            "cache_valid":
                self._cache_valid(),

            "remaining_requests":
                self.remaining_requests,

            "used_requests":
                self.used_requests,

            "last_error":
                self.last_error,
        }

    # ==========================================================
    # FECHAR SESSÃO
    # ==========================================================

    def close(
        self,
    ) -> None:
        """
        Fecha a sessão HTTP.
        """

        try:

            self.session.close()

        except Exception as exc:

            error(
                "Erro ao fechar sessão "
                f"da API: {exc}"
            )


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

api_client = OddsAPIClient()
