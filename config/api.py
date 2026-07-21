"""
OddReal 2.0

Módulo:
config/api.py

Configurações de APIs externas.

Responsável por:
- Chaves de acesso
- URLs
- Endpoints
- Parâmetros da API

Versão: 2.0
"""


from typing import Dict, Any

from datetime import datetime



class APIConfig:
    """
    Configuração central das APIs.
    """



    def __init__(self):

        self.version = "2.0"


        self.api_name = "The Odds API"


        self.api_key = ""


        self.base_url = (

            "https://api.the-odds-api.com/v4"

        )


        self.timeout = 15


        self.created_at = datetime.now()



    # ==================================================
    # INFORMAÇÕES DA API
    # ==================================================

    def info(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações básicas.
        """

        return {

            "name":

                self.api_name,


            "version":

                self.version,


            "base_url":

                self.base_url,


            "timeout":

                self.timeout,


            "configured":

                bool(
                    self.api_key
                )

        }



    # ==================================================
    # DEFINIR API KEY
    # ==================================================

    def set_key(
        self,
        key: str
    ) -> None:
        """
        Define chave da API.
        """

        self.api_key = key
      
    # ==================================================
    # ENDPOINTS DA API
    # ==================================================

    def endpoints(
        self
    ) -> Dict[str, str]:
        """
        Retorna endpoints disponíveis.
        """

        return {

            "sports":

                "/sports",


            "events":

                "/sports/{sport}/events",


            "odds":

                "/sports/{sport}/odds",


            "event_odds":

                "/sports/{sport}/events/{event_id}/odds"

        }



    # ==================================================
    # ENDPOINT DE ESPORTES
    # ==================================================

    def sports_endpoint(
        self
    ) -> str:
        """
        Endpoint de esportes.
        """

        return (

            f"{self.base_url}"
            "/sports"

        )



    # ==================================================
    # ENDPOINT DE EVENTOS
    # ==================================================

    def events_endpoint(
        self,
        sport: str
    ) -> str:
        """
        Endpoint de eventos.
        """

        return (

            f"{self.base_url}"
            f"/sports/{sport}/events"

        )



    # ==================================================
    # ENDPOINT DE ODDS
    # ==================================================

    def odds_endpoint(
        self,
        sport: str
    ) -> str:
        """
        Endpoint de odds.
        """

        return (

            f"{self.base_url}"
            f"/sports/{sport}/odds"

        )



    # ==================================================
    # ENDPOINT DE EVENTO ESPECÍFICO
    # ==================================================

    def event_odds_endpoint(
        self,
        sport: str,
        event_id: str
    ) -> str:
        """
        Endpoint de odds de uma partida.
        """

        return (

            f"{self.base_url}"
            f"/sports/{sport}/events/"
            f"{event_id}/odds"

        )
          # ==================================================
    # PARÂMETROS PADRÃO
    # ==================================================

    def default_params(
        self
    ) -> Dict[str, Any]:
        """
        Retorna parâmetros padrão
        das requisições.
        """

        return {

            "regions":

                "us",


            "markets":

                "h2h",


            "oddsFormat":

                "decimal",


            "dateFormat":

                "iso"

        }



    # ==================================================
    # REGIÕES DISPONÍVEIS
    # ==================================================

    def regions(
        self
    ) -> list:
        """
        Lista regiões aceitas.
        """

        return [

            "us",

            "uk",

            "eu",

            "au"

        ]



    # ==================================================
    # MERCADOS PADRÃO
    # ==================================================

    def markets(
        self
    ) -> list:
        """
        Mercados utilizados
        pelo OddReal.
        """

        return [

            "h2h",

            "spreads",

            "totals",

            "player_props"

        ]



    # ==================================================
    # FORMATO DE ODDS
    # ==================================================

    def odds_format(
        self
    ) -> Dict[str, str]:
        """
        Configura formato das odds.
        """

        return {

            "default":

                "decimal",


            "alternative":

                "american"

        }



    # ==================================================
    # FORMATO DE RESPOSTA
    # ==================================================

    def response_format(
        self
    ) -> Dict[str, Any]:
        """
        Configura tratamento
        da resposta.
        """

        return {

            "json":

                True,


            "validate":

                True,


            "normalize":

                True

        }
          # ==================================================
    # LIMITES DA API
    # ==================================================

    def limits(
        self
    ) -> Dict[str, Any]:
        """
        Retorna limites de utilização.
        """

        return {

            "requests_per_minute":

                60,


            "max_retries":

                3,


            "retry_delay":

                5,


            "timeout":

                self.timeout

        }



    # ==================================================
    # CONFIGURAÇÃO DE CACHE DA API
    # ==================================================

    def cache(
        self
    ) -> Dict[str, Any]:
        """
        Configuração de armazenamento
        temporário das respostas.
        """

        return {

            "enabled":

                True,


            "expiration":

                300,


            "store_odds":

                True,


            "store_events":

                True

        }



    # ==================================================
    # CONFIGURAÇÃO DE SEGURANÇA
    # ==================================================

    def security(
        self
    ) -> Dict[str, Any]:
        """
        Configurações de proteção
        da API Key.
        """

        return {

            "hide_key":

                True,


            "validate_key":

                True,


            "allow_empty_key":

                False

        }



    # ==================================================
    # CABEÇALHOS PADRÃO
    # ==================================================

    def headers(
        self
    ) -> Dict[str, str]:
        """
        Retorna cabeçalhos HTTP.
        """

        return {

            "Accept":

                "application/json",


            "Content-Type":

                "application/json"

        }



    # ==================================================
    # CONFIGURAÇÃO COMPLETA DA API
    # ==================================================

    def configuration(
        self
    ) -> Dict[str, Any]:
        """
        Retorna configuração completa.
        """

        return {

            "info":

                self.info(),


            "limits":

                self.limits(),


            "cache":

                self.cache(),


            "security":

                self.security()

        }
          # ==================================================
    # VALIDAR CONFIGURAÇÃO
    # ==================================================

    def validate(
        self
    ) -> Dict[str, Any]:
        """
        Verifica se a configuração
        da API está correta.
        """

        errors = []


        if not self.base_url:

            errors.append(
                "URL base não configurada"
            )



        if self.timeout <= 0:

            errors.append(
                "Timeout inválido"
            )



        if not self.api_key:

            errors.append(
                "API Key não configurada"
            )



        return {

            "valid":

                len(errors) == 0,


            "errors":

                errors

        }



    # ==================================================
    # MÁSCARA DA API KEY
    # ==================================================

    def masked_key(
        self
    ) -> str:
        """
        Oculta a chave para exibição.
        """

        if not self.api_key:

            return ""


        if len(self.api_key) <= 6:

            return "***"



        return (

            self.api_key[:3]

            +

            "***"

            +

            self.api_key[-3:]

        )



    # ==================================================
    # STATUS DA INTEGRAÇÃO
    # ==================================================

    def status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna status da API.
        """

        return {

            "service":

                "The Odds API",


            "configured":

                bool(
                    self.api_key
                ),


            "base_url":

                self.base_url,


            "timeout":

                self.timeout,


            "key":

                self.masked_key()

        }



    # ==================================================
    # TESTE DE CONFIGURAÇÃO
    # ==================================================

    def test(
        self
    ) -> bool:
        """
        Verifica se a API
        está pronta para uso.
        """

        result = self.validate()


        return result.get(
            "valid",
            False
        )
          # ==================================================
    # RESUMO DA API
    # ==================================================

    def summary(
        self
    ) -> Dict[str, Any]:
        """
        Retorna resumo da configuração.
        """

        return {

            "api":

                self.api_name,


            "version":

                self.version,


            "url":

                self.base_url,


            "configured":

                bool(
                    self.api_key
                ),


            "markets":

                self.markets()

        }



    # ==================================================
    # EXPORTAR CONFIGURAÇÃO
    # ==================================================

    def export(
        self
    ) -> Dict[str, Any]:
        """
        Exporta todas as configurações
        da API.
        """

        return {

            "info":

                self.info(),


            "endpoints":

                self.endpoints(),


            "parameters":

                self.default_params(),


            "limits":

                self.limits(),


            "cache":

                self.cache(),


            "exported_at":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # RESETAR CONFIGURAÇÃO
    # ==================================================

    def reset(
        self
    ) -> None:
        """
        Retorna valores padrão.
        """

        self.api_key = ""


        self.timeout = 15


        self.base_url = (

            "https://api.the-odds-api.com/v4"

        )



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

api_config = APIConfig()
