"""
OddReal 2.0
Comunicação com The Odds API.

Responsabilidades:
- comunicação com The Odds API;
- consulta de esportes;
- consulta de eventos e odds;
- consulta de odds de evento específico;
- cache das respostas;
- tratamento de erros;
- diagnóstico dos bookmakers recebidos;
- registro dos BOOKMAKER TITLE e BOOKMAKER KEY reais
  enviados pela The Odds API.

IMPORTANTE:
Este módulo NÃO decide quais bookmakers são autorizados.

A identificação/autorização dos bookmakers será feita
posteriormente pelo DataManager + configuração de bookmakers.

O objetivo aqui é preservar os dados reais retornados pela API
e registrar claramente seus identificadores para diagnóstico.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from config.settings import Settings
from modules.cache_manager import cache
from modules.logger import info, warning, error


class OddsAPI:
    """
    Cliente responsável pela comunicação com The Odds API.
    """

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self) -> None:
        self.api_key = Settings.API_KEY
        self.timeout = 20

        info(
            "OddsAPIClient OddReal 2.0 inicializado."
        )

    # ==========================================================
    # REQUEST
    # ==========================================================

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Executa uma requisição GET na The Odds API.

        Retorna:
            dados JSON retornados pela API

        Em caso de erro:
            {}
        """

        if params is None:
            params = {}

        request_params = dict(params)

        request_params["apiKey"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        try:

            response = requests.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )

            info(
                "The Odds API respondeu com "
                f"HTTP {response.status_code}."
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:

            error(
                "Timeout ao acessar "
                "The Odds API."
            )

            return {}

        except requests.exceptions.HTTPError as exc:

            error(
                f"Erro HTTP ao acessar "
                f"The Odds API: {exc}"
            )

            return {}

        except requests.exceptions.RequestException as exc:

            error(
                "Erro de conexão com "
                f"The Odds API: {exc}"
            )

            return {}

        except ValueError as exc:

            error(
                "The Odds API retornou "
                f"JSON inválido: {exc}"
            )

            return {}

        except Exception as exc:

            error(
                "Erro inesperado ao acessar "
                f"The Odds API: {exc}"
            )

            return {}

    # ==========================================================
    # DIAGNÓSTICO DOS BOOKMAKERS
    # ==========================================================

    def _log_bookmakers(
        self,
        events: Any,
    ) -> None:
        """
        Registra nos logs os bookmakers reais retornados
        pela The Odds API.

        Esta função NÃO filtra bookmakers.

        Ela serve exclusivamente para diagnóstico.

        Registra:

            title
            key

        e apresenta um resumo consolidado das keys encontradas.
        """

        if not isinstance(events, list):

            warning(
                "Não foi possível diagnosticar "
                "bookmakers: resposta de eventos "
                "não é uma lista."
            )

            return

        # ------------------------------------------------------
        # Estrutura para consolidar os bookmakers.
        #
        # key -> conjunto de títulos encontrados
        # ------------------------------------------------------

        bookmakers_found: Dict[
            str,
            set[str],
        ] = {}

        total_bookmakers = 0

        info(
            "=================================================="
        )

        info(
            "DIAGNÓSTICO DE BOOKMAKERS "
            "RECEBIDOS DA THE ODDS API"
        )

        info(
            "=================================================="
        )

        for event in events:

            if not isinstance(
                event,
                dict,
            ):
                continue

            home_team = event.get(
                "home_team",
                "",
            )

            away_team = event.get(
                "away_team",
                "",
            )

            event_name = (
                f"{home_team} x {away_team}"
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

            info(
                f"Evento: {event_name}"
            )

            if not bookmakers:

                info(
                    "  Nenhum bookmaker "
                    "retornado."
                )

                continue

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                total_bookmakers += 1

                title = str(
                    bookmaker.get(
                        "title",
                        "",
                    )
                    or ""
                ).strip()

                key = str(
                    bookmaker.get(
                        "key",
                        "",
                    )
                    or ""
                ).strip()

                # --------------------------------------------------
                # Registra o valor REAL recebido.
                # --------------------------------------------------

                info(
                    "  BOOKMAKER "
                    f"title='{title}' "
                    f"| key='{key}'"
                )

                # --------------------------------------------------
                # Consolidação.
                # --------------------------------------------------

                if key:

                    if key not in bookmakers_found:

                        bookmakers_found[key] = set()

                    if title:

                        bookmakers_found[
                            key
                        ].add(
                            title
                        )

        # ======================================================
        # RESUMO
        # ======================================================

        info(
            "=================================================="
        )

        info(
            "RESUMO DOS BOOKMAKERS RECEBIDOS"
        )

        info(
            "=================================================="
        )

        if not bookmakers_found:

            warning(
                "Nenhuma bookmaker com key "
                "válida foi encontrada na resposta."
            )

            return

        for key in sorted(
            bookmakers_found.keys()
        ):

            titles = sorted(
                bookmakers_found[key]
            )

            if titles:

                title_text = ", ".join(
                    titles
                )

                info(
                    f"KEY='{key}' "
                    f"| TITLE='{title_text}'"
                )

            else:

                info(
                    f"KEY='{key}' "
                    "| TITLE não informado"
                )

        info(
            "Total de ocorrências de bookmakers "
            f"recebidas: {total_bookmakers}"
        )

        info(
            "Total de bookmaker keys únicas: "
            f"{len(bookmakers_found)}"
        )

        info(
            "=================================================="
        )

    # ==========================================================
    # ESPORTES
    # ==========================================================

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
                "A lista de esportes retornada "
                "pela API não é válida."
            )

            return []

        cache.set(
            cache_key,
            sports,
            ttl=3600,
        )

        info(
            f"{len(sports)} esportes "
            "recebidos da The Odds API."
        )

        return sports

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def get_events(
        self,
        sport: str,
    ) -> List[Dict[str, Any]]:
        """
        Retorna eventos e odds de determinado esporte.

        Neste estágio o método NÃO filtra bookmakers.

        Todos os bookmakers retornados pela API são preservados.

        O objetivo é permitir que o DataManager faça posteriormente
        a filtragem através da lista branca.
        """

        if not sport:

            warning(
                "get_events recebeu esporte vazio."
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
                f"Eventos de '{sport}' "
                "carregados do cache."
            )

            # Mesmo usando cache, fazemos o diagnóstico
            # dos bookmakers presentes no objeto armazenado.

            self._log_bookmakers(
                cached
            )

            return cached

        info(
            "Consultando eventos de "
            f"'{sport}' na The Odds API."
        )

        endpoint = (
            f"sports/{sport}/odds"
        )

        # ------------------------------------------------------
        # IMPORTANTE
        #
        # Não colocamos filtro de bookmaker aqui.
        #
        # A API entrega os bookmakers.
        # A camada de negócio decide posteriormente
        # quais serão autorizados.
        # ------------------------------------------------------

        params = {
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
        }

        data = self._request(
            endpoint,
            params,
        )

        if not isinstance(
            data,
            list,
        ):

            warning(
                f"A API não retornou uma lista "
                f"de eventos para '{sport}'."
            )

            return []

        cache.set(
            cache_key,
            data,
            ttl=120,
        )

        info(
            f"{len(data)} eventos recebidos "
            "da The Odds API."
        )

        # ======================================================
        # DIAGNÓSTICO REAL
        # ======================================================

        self._log_bookmakers(
            data
        )

        # ======================================================
        # DIAGNÓSTICO INDIVIDUAL DOS EVENTOS
        # ======================================================

        for event in data:

            if not isinstance(
                event,
                dict,
            ):
                continue

            home_team = event.get(
                "home_team",
                "",
            )

            away_team = event.get(
                "away_team",
                "",
            )

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):

                bookmakers = []

            info(
                "Evento "
                f"{home_team} x {away_team} "
                f"recebeu "
                f"{len(bookmakers)} "
                "bookmakers da API."
            )

        return data

    # ==========================================================
    # ODDS DE EVENTO ESPECÍFICO
    # ==========================================================

    def get_event_odds(
        self,
        sport: str,
        event_id: str,
    ) -> Dict[str, Any]:
        """
        Retorna odds detalhadas de um evento específico.
        """

        if not sport:

            warning(
                "get_event_odds recebeu "
                "sport vazio."
            )

            return {}

        if not event_id:

            warning(
                "get_event_odds recebeu "
                "event_id vazio."
            )

            return {}

        endpoint = (
            f"sports/{sport}/events/"
            f"{event_id}/odds"
        )

        params = {
            "regions": "eu",
            "markets": (
                "h2h,spreads,totals"
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

            warning(
                "Resposta inválida ao "
                "consultar odds do evento "
                f"{event_id}."
            )

            return {}

        # ------------------------------------------------------
        # A resposta individual normalmente possui bookmakers.
        # Fazemos o mesmo diagnóstico sem alterar os dados.
        # ------------------------------------------------------

        bookmakers = data.get(
            "bookmakers",
            [],
        )

        if isinstance(
            bookmakers,
            list,
        ):

            self._log_bookmakers(
                [
                    {
                        "id": event_id,
                        "home_team": data.get(
                            "home_team",
                            "",
                        ),
                        "away_team": data.get(
                            "away_team",
                            "",
                        ),
                        "bookmakers": bookmakers,
                    }
                ]
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
