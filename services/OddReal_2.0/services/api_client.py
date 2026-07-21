"""
OddReal 2.0

Módulo:
services/api_client.py

Cliente de comunicação
com APIs externas.

Responsável por:
- Requisições HTTP
- Autenticação
- Tratamento de erros
- Integração com cache

Versão: 2.0
"""


from typing import Dict, Any, Optional

from datetime import datetime

import requests



class APIClient:
    """
    Cliente principal de comunicação externa.
    """



    def __init__(
        self,
        api_key: str,
        base_url: str
    ):

        self.version = "2.0"


        self.api_key = api_key


        self.base_url = base_url.rstrip(
            "/"
        )


        self.session = requests.Session()


        self.timeout = 15


        self.created_at = datetime.now()



    # ==================================================
    # CABEÇALHOS DA REQUISIÇÃO
    # ==================================================

    def headers(
        self
    ) -> Dict[str, str]:
        """
        Retorna cabeçalhos padrão.
        """

        return {

            "Accept":
                "application/json",


            "Content-Type":
                "application/json"

        }



    # ==================================================
    # CONSTRUÇÃO DE URL
    # ==================================================

    def build_url(
        self,
        endpoint: str
    ) -> str:
        """
        Monta URL final da API.
        """

        return (

            f"{self.base_url}/"
            f"{endpoint.lstrip('/')}"

        )



    # ==================================================
    # REQUISIÇÃO GET BÁSICA
    # ==================================================

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa uma requisição GET.
        """

        url = self.build_url(
            endpoint
        )


        response = self.session.get(

            url,

            params=params,

            headers=self.headers(),

            timeout=self.timeout

        )


        return self.handle_response(
            response
      )
          # ==================================================
    # ADICIONAR API KEY NOS PARÂMETROS
    # ==================================================

    def authenticate_params(
        self,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adiciona a chave da API
        aos parâmetros da requisição.
        """

        if params is None:

            params = {}


        params["apiKey"] = self.api_key


        return params



    # ==================================================
    # GET AUTENTICADO
    # ==================================================

    def authenticated_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa GET com autenticação.
        """

        params = (
            self.authenticate_params(
                params
            )
        )


        return self.get(
            endpoint,
            params
        )



    # ==================================================
    # TRATAMENTO DE RESPOSTA
    # ==================================================

    def handle_response(
        self,
        response
    ) -> Dict[str, Any]:
        """
        Padroniza respostas HTTP.
        """

        status = (
            response.status_code
        )


        if status == 200:

            try:

                return {

                    "success":

                        True,


                    "data":

                        response.json(),


                    "status_code":

                        status

                }


            except Exception:

                return {

                    "success":

                        False,


                    "error":

                        "Resposta JSON inválida",


                    "status_code":

                        status

                }



        elif status == 401:

            return {

                "success":

                    False,


                "error":

                    "API Key inválida",


                "status_code":

                    status

            }



        elif status == 429:

            return {

                "success":

                    False,


                "error":

                    "Limite de requisições atingido",


                "status_code":

                    status

            }



        else:

            return {

                "success":

                    False,


                "error":

                    f"Erro HTTP {status}",


                "status_code":

                    status

            }



    # ==================================================
    # TRATAMENTO DE EXCEÇÕES
    # ==================================================

    def safe_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GET protegido contra falhas.
        """

        try:

            return self.authenticated_get(
                endpoint,
                params
            )


        except requests.exceptions.Timeout:

            return {

                "success":

                    False,


                "error":

                    "Tempo limite excedido"

            }



        except requests.exceptions.ConnectionError:

            return {

                "success":

                    False,


                "error":

                    "Falha de conexão"

            }



        except Exception as error:

            return {

                "success":

                    False,


                "error":

                    str(error)

      }
              # ==================================================
    # LISTAR ESPORTES DISPONÍVEIS
    # ==================================================

    def get_sports(
        self
    ) -> Dict[str, Any]:
        """
        Retorna esportes disponíveis
        na API.
        """

        return self.safe_get(

            "sports"

        )



    # ==================================================
    # BUSCAR EVENTOS
    # ==================================================

    def get_events(
        self,
        sport: str
    ) -> Dict[str, Any]:
        """
        Busca eventos de um esporte.
        """

        endpoint = (

            f"sports/{sport}/events"

        )


        return self.safe_get(

            endpoint

        )



    # ==================================================
    # BUSCAR ODDS
    # ==================================================

    def get_odds(
        self,
        sport: str,
        regions: str = "us",
        markets: str = "h2h"
    ) -> Dict[str, Any]:
        """
        Busca odds de um esporte.
        """

        endpoint = (

            f"sports/{sport}/odds"

        )


        params = {

            "regions":

                regions,


            "markets":

                markets

        }


        return self.safe_get(

            endpoint,

            params

        )



    # ==================================================
    # BUSCAR ODDS DE EVENTO ESPECÍFICO
    # ==================================================

    def get_event_odds(
        self,
        sport: str,
        event_id: str,
        markets: str = "h2h"
    ) -> Dict[str, Any]:
        """
        Busca odds de uma partida específica.
        """

        endpoint = (

            f"sports/{sport}/events/"
            f"{event_id}/odds"

        )


        params = {

            "markets":

                markets

        }


        return self.safe_get(

            endpoint,

            params

        )



    # ==================================================
    # BUSCAR MÚLTIPLOS MERCADOS
    # ==================================================

    def get_markets(
        self,
        sport: str,
        markets: str
    ) -> Dict[str, Any]:
        """
        Busca mercados específicos.
        """

        endpoint = (

            f"sports/{sport}/odds"

        )


        params = {

            "markets":

                markets

        }


        return self.safe_get(

            endpoint,

            params

        )
          # ==================================================
    # IMPORTAR CACHE
    # ==================================================

    def set_cache(
        self,
        cache_manager
    ) -> None:
        """
        Conecta o cliente API
        ao sistema de cache.
        """

        self.cache = cache_manager



    # ==================================================
    # BUSCAR COM CACHE
    # ==================================================

    def cached_get(
        self,
        key: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa busca utilizando cache.
        """

        if hasattr(
            self,
            "cache"
        ):

            cached = self.cache.get(
                key
            )


            if cached is not None:

                return {

                    "success":

                        True,


                    "data":

                        cached,


                    "cached":

                        True

                }



        response = self.safe_get(
            endpoint,
            params
        )


        if (
            response.get(
                "success"
            )
            and
            hasattr(
                self,
                "cache"
            )
        ):

            self.cache.set(

                key,

                response.get(
                    "data"
                )

            )



        response["cached"] = False


        return response



    # ==================================================
    # ESPORTES COM CACHE
    # ==================================================

    def cached_sports(
        self
    ) -> Dict[str, Any]:
        """
        Busca esportes usando cache.
        """

        return self.cached_get(

            "api:sports",

            "sports"

        )



    # ==================================================
    # EVENTOS COM CACHE
    # ==================================================

    def cached_events(
        self,
        sport: str
    ) -> Dict[str, Any]:
        """
        Busca eventos com cache.
        """

        key = (

            f"api:events:"
            f"{sport}"

        )


        endpoint = (

            f"sports/{sport}/events"

        )


        return self.cached_get(

            key,

            endpoint

        )



    # ==================================================
    # ODDS COM CACHE
    # ==================================================

    def cached_odds(
        self,
        sport: str,
        markets: str = "h2h"
    ) -> Dict[str, Any]:
        """
        Busca odds utilizando cache.
        """

        key = (

            f"api:odds:"
            f"{sport}:"
            f"{markets}"

        )


        endpoint = (

            f"sports/{sport}/odds"

        )


        params = {

            "markets":

                markets

        }


        return self.cached_get(

            key,

            endpoint,

            params

        )
          # ==================================================
    # VALIDAR RESPOSTA DA API
    # ==================================================

    def validate_data(
        self,
        data: Any
    ) -> bool:
        """
        Verifica se os dados
        recebidos são válidos.
        """

        if data is None:

            return False



        if isinstance(
            data,
            dict
        ):

            return len(data) > 0



        if isinstance(
            data,
            list
        ):

            return len(data) > 0



        return True



    # ==================================================
    # NORMALIZAR RESPOSTA
    # ==================================================

    def normalize_response(
        self,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Padroniza retorno da API.
        """

        if not response.get(
            "success",
            False
        ):

            return response



        data = response.get(
            "data"
        )


        return {

            "success":

                True,


            "valid":

                self.validate_data(
                    data
                ),


            "data":

                data,


            "cached":

                response.get(
                    "cached",
                    False
                ),


            "timestamp":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # REGISTRAR CHAMADA
    # ==================================================

    def log_request(
        self,
        endpoint: str,
        success: bool
    ) -> Dict[str, Any]:
        """
        Cria registro de chamada.
        """

        return {

            "endpoint":

                endpoint,


            "success":

                success,


            "time":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # EXECUÇÃO CONTROLADA
    # ==================================================

    def request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Método principal de requisição.
        """

        response = self.safe_get(

            endpoint,

            params

        )


        normalized = (
            self.normalize_response(
                response
            )
        )


        self.last_request = (
            self.log_request(

                endpoint,

                normalized.get(
                    "success",
                    False
                )

            )
        )


        return normalized



    # ==================================================
    # ÚLTIMA REQUISIÇÃO
    # ==================================================

    def last_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna status da última chamada.
        """

        return getattr(

            self,

            "last_request",

            {}
          

    )

    # ==================================================
    # STATUS DO CLIENTE
    # ==================================================

    def service_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do serviço API.
        """

        return {

            "service":

                "api_client",


            "module":

                "services.api_client",


            "version":

                self.version,


            "base_url":

                self.base_url,


            "initialized":

                True,


            "created_at":

                self.created_at.isoformat()

        }



    # ==================================================
    # TESTE DE CONEXÃO
    # ==================================================

    def connection_test(
        self
    ) -> Dict[str, Any]:
        """
        Testa comunicação com a API.
        """

        try:

            response = self.get_sports()


            return {

                "online":

                    response.get(
                        "success",
                        False
                    ),


                "response":

                    response

            }


        except Exception as error:

            return {

                "online":

                    False,


                "error":

                    str(error)

            }



    # ==================================================
    # FECHAMENTO DA SESSÃO
    # ==================================================

    def close(
        self
    ) -> None:
        """
        Encerra sessão HTTP.
        """

        self.session.close()



# ======================================================
# CONFIGURAÇÃO PADRÃO
# ======================================================

DEFAULT_API_URL = (

    "https://api.the-odds-api.com/v4"

)



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

api_client = APIClient(

    api_key="",

    base_url=DEFAULT_API_URL

)
