"""
OddReal 2.0
Comunicação com The Odds API

Responsabilidades:

- Comunicação com The Odds API
- Consulta de esportes
- Consulta de eventos
- Consulta de odds
- Tratamento de erros
- Cache
- Diagnóstico dos bookmakers recebidos
- Registro das bookmaker keys reais nos logs

IMPORTANTE:

Este módulo NÃO decide sozinho quais bookmakers serão usados
na análise.

Ele apenas:
    1. consulta a API;
    2. registra exatamente o que a API devolveu;
    3. entrega os dados ao restante do sistema.

O filtro de bookmakers autorizados deve ser realizado pela
camada de normalização/DataManager/Analyzer.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any

import requests

from config.settings import Settings
from modules.cache_manager import cache
from modules.logger import info, warning, error


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

BASE_URL = "https://api.the-odds-api.com/v4"

# Alterar esta versão força uma nova chave de cache.
#
# Isso é importante durante o diagnóstico para evitar que
# dados antigos continuem sendo utilizados.
CACHE_VERSION = "diagnostic-v3"


# ==========================================================
# CLIENTE
# ==========================================================

class OddsAPI:
    """
    Cliente responsável pela comunicação com a The Odds API.
    """

    BASE_URL = BASE_URL

    def __init__(self) -> None:

        self.api_key = Settings.API_KEY
        self.timeout = 20

        info(
            "OddsAPIClient OddReal 2.0 inicializado."
        )

        # --------------------------------------------------
        # Nunca registrar a API KEY no log.
        # --------------------------------------------------

        if not self.api_key:

            warning(
                "The Odds API: API_KEY não configurada."
            )

        else:

            info(
                "The Odds API: API_KEY carregada "
                "corretamente da configuração."
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

        A API KEY nunca é registrada nos logs.
        """

        if params is None:

            params = {}

        # Criamos uma cópia para não alterar o dicionário
        # recebido pelo chamador.

        request_params = dict(params)

        request_params["apiKey"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        # --------------------------------------------------
        # LOG DA REQUISIÇÃO
        # --------------------------------------------------

        safe_params = dict(request_params)

        # Nunca mostrar a API KEY.

        safe_params["apiKey"] = "***"

        info(
            "The Odds API requisitando: "
            f"{endpoint} | "
            f"params={safe_params}"
        )

        try:

            response = requests.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )

            # --------------------------------------------------
            # STATUS HTTP
            # --------------------------------------------------

            info(
                "The Odds API respondeu com HTTP "
                f"{response.status_code}."
            )

            response.raise_for_status()

            data = response.json()

            return data

        # ------------------------------------------------------
        # TIMEOUT
        # ------------------------------------------------------

        except requests.exceptions.Timeout:

            error(
                "Timeout ao acessar The Odds API."
            )

            return {}

        # ------------------------------------------------------
        # ERRO HTTP
        # ------------------------------------------------------

        except requests.exceptions.HTTPError as exc:

            error(
                f"Erro HTTP na The Odds API: {exc}"
            )

            # Tenta mostrar o corpo da resposta porque pode
            # conter uma explicação útil da própria API.

            try:

                body = response.text[:1000]

                error(
                    "Resposta da The Odds API: "
                    f"{body}"
                )

            except Exception:

                pass

            return {}

        # ------------------------------------------------------
        # ERRO DE JSON
        # ------------------------------------------------------

        except ValueError as exc:

            error(
                "A The Odds API retornou uma resposta "
                f"que não pôde ser convertida em JSON: {exc}"
            )

            return {}

        # ------------------------------------------------------
        # ERRO GERAL
        # ------------------------------------------------------

        except Exception as exc:

            error(
                "Erro inesperado ao acessar "
                f"The Odds API: {exc}"
            )

            return {}

    # ======================================================
    # DIAGNÓSTICO DE BOOKMAKERS
    # ======================================================

    @staticmethod
    def _log_bookmakers(
        events: List[Dict[str, Any]],
    ) -> None:
        """
        Registra nos logs as bookmaker keys REAIS retornadas
        pela The Odds API.

        Este método é exclusivamente diagnóstico.

        Exemplo de log:

            Evento X:
            bookmaker key='bet365'
            title='Bet365'

        Dessa maneira conseguimos descobrir exatamente
        quais identificadores a API está enviando.
        """

        if not events:

            warning(
                "Diagnóstico de bookmakers: "
                "nenhum evento recebido."
            )

            return

        info(
            "=================================================="
        )

        info(
            "DIAGNÓSTICO DE BOOKMAKERS — KEYS REAIS DA API"
        )

        info(
            "=================================================="
        )

        all_keys = set()

        # --------------------------------------------------
        # PERCORRE EVENTOS
        # --------------------------------------------------

        for event in events:

            event_id = event.get(
                "id",
                "sem-id",
            )

            home_team = event.get(
                "home_team",
                "?",
            )

            away_team = event.get(
                "away_team",
                "?",
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            info(
                f"Evento: {home_team} x {away_team} "
                f"| ID={event_id}"
            )

            # --------------------------------------------------
            # EVENTO SEM BOOKMAKERS
            # --------------------------------------------------

            if not bookmakers:

                warning(
                    f"Evento {home_team} x {away_team}: "
                    "nenhum bookmaker retornado."
                )

                continue

            event_keys = []

            # --------------------------------------------------
            # BOOKMAKERS
            # --------------------------------------------------

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):

                    warning(
                        "Bookmaker recebido em formato "
                        f"inesperado: {bookmaker!r}"
                    )

                    continue

                key = bookmaker.get(
                    "key"
                )

                title = bookmaker.get(
                    "title"
                )

                last_update = bookmaker.get(
                    "last_update"
                )

                if key:

                    all_keys.add(
                        str(key)
                    )

                    event_keys.append(
                        str(key)
                    )

                info(
                    "  BOOKMAKER | "
                    f"key='{key}' | "
                    f"title='{title}' | "
                    f"last_update='{last_update}'"
                )

            info(
                "  KEYS DO EVENTO: "
                f"{sorted(set(event_keys))}"
            )

        # --------------------------------------------------
        # RESUMO GLOBAL
        # --------------------------------------------------

        info(
            "--------------------------------------------------"
        )

        info(
            "BOOKMAKER KEYS ÚNICAS RECEBIDAS PELA API:"
        )

        if all_keys:

            for key in sorted(all_keys):

                info(
                    f"  -> '{key}'"
                )

        else:

            warning(
                "Nenhuma bookmaker key foi encontrada."
            )

        info(
            "TOTAL DE BOOKMAKER KEYS ÚNICAS: "
            f"{len(all_keys)}"
        )

        info(
            "=================================================="
        )

    # ======================================================
    # DIAGNÓSTICO DE MERCADOS
    # ======================================================

    @staticmethod
    def _log_markets(
        events: List[Dict[str, Any]],
    ) -> None:
        """
        Registra os mercados realmente retornados pela API.

        Isso permite descobrir se o problema está:

            bookmakers
                ou
            markets
                ou
            outcomes.
        """

        info(
            "=================================================="
        )

        info(
            "DIAGNÓSTICO DE MERCADOS DA THE ODDS API"
        )

        info(
            "=================================================="
        )

        for event in events:

            home_team = event.get(
                "home_team",
                "?",
            )

            away_team = event.get(
                "away_team",
                "?",
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):

                    continue

                bookmaker_key = bookmaker.get(
                    "key",
                    "sem-key",
                )

                markets = bookmaker.get(
                    "markets",
                    [],
                )

                if not markets:

                    info(
                        f"Evento {home_team} x {away_team} | "
                        f"bookmaker='{bookmaker_key}' | "
                        "nenhum mercado."
                    )

                    continue

                market_keys = []

                for market in markets:

                    if not isinstance(
                        market,
                        dict,
                    ):

                        continue

                    market_key = market.get(
                        "key"
                    )

                    if market_key:

                        market_keys.append(
                            str(market_key)
                        )

                info(
                    f"Evento {home_team} x {away_team} | "
                    f"bookmaker='{bookmaker_key}' | "
                    f"markets={sorted(set(market_keys))}"
                )

        info(
            "=================================================="
        )

    # ======================================================
    # SPORTS
    # ======================================================

    def get_sports(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Retorna a lista de esportes disponíveis.
        """

        cache_key = (
            f"{CACHE_VERSION}:sports"
        )

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                "Sports carregados do cache."
            )

            return cached

        info(
            "Consultando lista de esportes "
            "na The Odds API."
        )

        sports = self._request(
            "sports"
        )

        if not isinstance(
            sports,
            list,
        ):

            warning(
                "Resposta inesperada ao consultar esportes."
            )

            return []

        cache.set(
            cache_key,
            sports,
            ttl=3600,
        )

        info(
            "The Odds API retornou "
            f"{len(sports)} esportes."
        )

        return sports

    # ======================================================
    # EVENTOS
    # ======================================================

    def get_events(
        self,
        sport: str,
    ) -> List[Dict[str, Any]]:
        """
        Consulta eventos e odds de um esporte.

        IMPORTANTE:

        O diagnóstico registra as bookmaker keys reais
        devolvidas pela API antes de qualquer filtragem.
        """

        if not sport:

            warning(
                "get_events recebeu sport vazio."
            )

            return []

        cache_key = (
            f"{CACHE_VERSION}:events:{sport}"
        )

        cached = cache.get(
            cache_key
        )

        if cached:

            info(
                f"Eventos de '{sport}' "
                "carregados do cache."
            )

            # Também registra o conteúdo do cache,
            # pois precisamos saber exatamente o que está
            # chegando ao DataManager.

            if isinstance(
                cached,
                list,
            ):

                self._log_bookmakers(
                    cached
                )

            return cached

        # --------------------------------------------------
        # CONSULTA
        # --------------------------------------------------

        endpoint = (
            f"sports/{sport}/odds"
        )

        params = {
            # Região usada pela consulta.
            #
            # Mantemos EU por enquanto para não alterar
            # silenciosamente o comportamento atual.
            "regions": "eu",

            # Mercado principal.
            "markets": "h2h",

            # Odds decimais.
            "oddsFormat": "decimal",
        }

        info(
            f"Consultando eventos para sport='{sport}'."
        )

        data = self._request(
            endpoint,
            params,
        )

        # --------------------------------------------------
        # VALIDAÇÃO
        # --------------------------------------------------

        if not isinstance(
            data,
            list,
        ):

            warning(
                "A The Odds API não retornou uma lista "
                "de eventos."
            )

            return []

        info(
            "The Odds API retornou "
            f"{len(data)} eventos."
        )

        # --------------------------------------------------
        # DIAGNÓSTICO ANTES DO DATA MANAGER
        # --------------------------------------------------

        self._log_bookmakers(
            data
        )

        self._log_markets(
            data
        )

        # --------------------------------------------------
        # CACHE
        # --------------------------------------------------

        cache.set(
            cache_key,
            data,
            ttl=120,
        )

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        for event in data:

            home_team = event.get(
                "home_team",
                "?",
            )

            away_team = event.get(
                "away_team",
                "?",
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            info(
                f"Evento {home_team} x {away_team} "
                f"recebeu {len(bookmakers)} bookmakers "
                "da API."
            )

        return data

    # ======================================================
    # ODDS DE EVENTO ESPECÍFICO
    # ======================================================

    def get_event_odds(
        self,
        sport: str,
        event_id: str,
    ) -> Dict[str, Any]:
        """
        Consulta odds detalhadas de um evento específico.
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
            "Consultando odds detalhadas: "
            f"sport='{sport}' | "
            f"event_id='{event_id}'"
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
                "Resposta inesperada ao consultar "
                "odds detalhadas."
            )

            return {}

        # --------------------------------------------------
        # DIAGNÓSTICO DO EVENTO
        # --------------------------------------------------

        bookmakers = data.get(
            "bookmakers",
            [],
        )

        info(
            "Evento específico retornou "
            f"{len(bookmakers)} bookmakers."
        )

        # --------------------------------------------------
        # REGISTRA KEYS
        # --------------------------------------------------

        self._log_bookmakers(
            [data]
        )

        self._log_markets(
            [data]
        )

        return data


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

api = OddsAPI()


# ==========================================================
# EXPORTAÇÃO
# ==========================================================

__all__ = [
    "OddsAPI",
    "api",
                ]
