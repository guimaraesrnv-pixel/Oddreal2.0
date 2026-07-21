"""
OddReal 2.0

Módulo:
services/cache.py

Sistema de cache interno.

Responsável por:
- Armazenamento temporário
- Controle de expiração
- Redução de chamadas externas

Versão: 2.0
"""

from typing import Dict, Any
from datetime import datetime, timedelta



class CacheManager:
    """
    Gerenciador de cache do sistema.
    """



    def __init__(
        self,
        expiration_minutes: int = 15
    ):

        self.version = "2.0"

        self.expiration = timedelta(
            minutes=expiration_minutes
        )

        self.storage = {}



    # ==================================================
    # INSERIR DADOS NO CACHE
    # ==================================================

    def set(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Armazena informação no cache.
        """

        self.storage[key] = {

            "value":
                value,

            "created_at":
                datetime.now()

        }



    # ==================================================
    # BUSCAR DADOS DO CACHE
    # ==================================================

    def get(
        self,
        key: str
    ) -> Any:
        """
        Recupera informação armazenada.
        """

        if key not in self.storage:

            return None



        item = self.storage[key]


        if self.is_expired(
            item
        ):

            self.delete(
                key
            )

            return None



        return item["value"]



    # ==================================================
    # VERIFICAR EXPIRAÇÃO
    # ==================================================

    def is_expired(
        self,
        item: Dict[str, Any]
    ) -> bool:
        """
        Verifica validade do cache.
        """

        created = item.get(
            "created_at"
        )


        if not created:

            return True



        return (

            datetime.now()
            -
            created

        ) > self.expiration
          # ==================================================
    # ATUALIZAR CACHE
    # ==================================================

    def update(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Atualiza um valor existente
        no cache.
        """

        self.set(
            key,
            value
        )



    # ==================================================
    # DELETAR ITEM DO CACHE
    # ==================================================

    def delete(
        self,
        key: str
    ) -> bool:
        """
        Remove item específico
        do cache.
        """

        if key in self.storage:

            del self.storage[key]

            return True



        return False



    # ==================================================
    # LIMPAR TODO O CACHE
    # ==================================================

    def clear(
        self
    ) -> None:
        """
        Remove todos os dados
        armazenados.
        """

        self.storage.clear()



    # ==================================================
    # LIMPEZA AUTOMÁTICA
    # ==================================================

    def cleanup(
        self
    ) -> int:
        """
        Remove automaticamente
        itens expirados.

        Retorna quantidade removida.
        """

        removed = 0


        keys = list(
            self.storage.keys()
        )


        for key in keys:

            if self.is_expired(
                self.storage[key]
            ):

                self.delete(
                    key
                )

                removed += 1



        return removed



    # ==================================================
    # VERIFICAR EXISTÊNCIA
    # ==================================================

    def exists(
        self,
        key: str
    ) -> bool:
        """
        Verifica se existe dado válido.
        """

        value = self.get(
            key
        )


        return value is not None
          # ==================================================
    # CRIAÇÃO DE CHAVE DE CACHE
    # ==================================================

    def create_key(
        self,
        prefix: str,
        identifier: str
    ) -> str:
        """
        Cria uma chave padronizada
        para armazenamento.
        """

        return (

            f"{prefix}:"
            f"{identifier}"

        )



    # ==================================================
    # CACHE DE EVENTO
    # ==================================================

    def event_key(
        self,
        sport: str,
        event_id: str
    ) -> str:
        """
        Cria chave específica
        para partidas.
        """

        return self.create_key(

            "event",

            f"{sport}:{event_id}"

        )



    # ==================================================
    # CACHE DE ODDS
    # ==================================================

    def odds_key(
        self,
        event_id: str
    ) -> str:
        """
        Cria chave para odds
        de um evento.
        """

        return self.create_key(

            "odds",

            event_id

        )



    # ==================================================
    # CACHE DE MERCADOS
    # ==================================================

    def market_key(
        self,
        event_id: str
    ) -> str:
        """
        Cria chave para mercados.
        """

        return self.create_key(

            "market",

            event_id

        )



    # ==================================================
    # CACHE DE API
    # ==================================================

    def api_key(
        self,
        endpoint: str,
        params: str = ""
    ) -> str:
        """
        Cria chave baseada
        em chamada de API.
        """

        return self.create_key(

            "api",

            f"{endpoint}:{params}"

        )



    # ==================================================
    # SALVAR EVENTO
    # ==================================================

    def cache_event(
        self,
        sport: str,
        event_id: str,
        data: Any
    ) -> None:
        """
        Armazena dados de uma partida.
        """

        key = self.event_key(

            sport,

            event_id

        )


        self.set(

            key,

            data

        )



    # ==================================================
    # RECUPERAR EVENTO
    # ==================================================

    def get_event(
        self,
        sport: str,
        event_id: str
    ) -> Any:
        """
        Recupera partida armazenada.
        """

        key = self.event_key(

            sport,

            event_id

        )


        return self.get(
          key
    )
          # ==================================================
    # SALVAR ODDS
    # ==================================================

    def cache_odds(
        self,
        event_id: str,
        odds: Any
    ) -> None:
        """
        Armazena odds de um evento.
        """

        key = self.odds_key(
            event_id
        )


        self.set(
            key,
            odds
        )



    # ==================================================
    # RECUPERAR ODDS
    # ==================================================

    def get_odds(
        self,
        event_id: str
    ) -> Any:
        """
        Recupera odds armazenadas.
        """

        key = self.odds_key(
            event_id
        )


        return self.get(
            key
        )



    # ==================================================
    # SALVAR MERCADOS
    # ==================================================

    def cache_markets(
        self,
        event_id: str,
        markets: Any
    ) -> None:
        """
        Armazena mercados de aposta.
        """

        key = self.market_key(
            event_id
        )


        self.set(
            key,
            markets
        )



    # ==================================================
    # RECUPERAR MERCADOS
    # ==================================================

    def get_markets(
        self,
        event_id: str
    ) -> Any:
        """
        Recupera mercados.
        """

        key = self.market_key(
            event_id
        )


        return self.get(
            key
        )



    # ==================================================
    # CACHE TEMPORÁRIO
    # ==================================================

    def temporary_store(
        self,
        name: str,
        data: Any,
        minutes: int = 5
    ) -> None:
        """
        Armazena informação temporária
        com validade personalizada.
        """

        old_expiration = self.expiration


        self.expiration = timedelta(
            minutes=minutes
        )


        self.set(
            name,
            data
        )


        self.expiration = old_expiration



    # ==================================================
    # TAMANHO DO CACHE
    # ==================================================

    def size(
        self
    ) -> int:
        """
        Retorna quantidade de itens
        armazenados.
        """

        return len(
            self.storage
        )



    # ==================================================
    # LISTAR CHAVES
    # ==================================================

    def keys(
        self
    ) -> list:
        """
        Retorna todas as chaves atuais.
        """

        return list(
            self.storage.keys()
        )
          # ==================================================
    # ESTATÍSTICAS DO CACHE
    # ==================================================

    def statistics(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações gerais
        do sistema de cache.
        """

        total = len(
            self.storage
        )


        expired = 0


        for item in self.storage.values():

            if self.is_expired(
                item
            ):

                expired += 1



        return {

            "total_items":

                total,


            "active_items":

                total - expired,


            "expired_items":

                expired,


            "expiration_minutes":

                self.expiration
                .seconds
                //
                60

        }



    # ==================================================
    # VERIFICAR SAÚDE DO CACHE
    # ==================================================

    def health_check(
        self
    ) -> Dict[str, Any]:
        """
        Verifica estado do cache.
        """

        return {

            "status":

                "online",


            "storage_available":

                True,


            "items":

                len(
                    self.storage
                ),


            "timestamp":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # REMOVER POR PREFIXO
    # ==================================================

    def delete_by_prefix(
        self,
        prefix: str
    ) -> int:
        """
        Remove todos os registros
        de determinado tipo.

        Exemplo:

        event:
        odds:
        market:
        """

        removed = 0


        keys = list(
            self.storage.keys()
        )


        for key in keys:

            if key.startswith(
                prefix
            ):

                self.delete(
                    key
                )

                removed += 1



        return removed



    # ==================================================
    # LIMPEZA POR TIPO
    # ==================================================

    def clear_events(
        self
    ) -> int:
        """
        Remove apenas eventos.
        """

        return self.delete_by_prefix(
            "event:"
        )



    def clear_odds(
        self
    ) -> int:
        """
        Remove apenas odds.
        """

        return self.delete_by_prefix(
            "odds:"
        )



    def clear_markets(
        self
    ) -> int:
        """
        Remove apenas mercados.
        """

        return self.delete_by_prefix(
            "market:"
        )
          # ==================================================
    # EXPORTAR CACHE
    # ==================================================

    def export_data(
        self
    ) -> Dict[str, Any]:
        """
        Exporta o conteúdo atual
        do cache.
        """

        return self.storage.copy()



    # ==================================================
    # IMPORTAR CACHE
    # ==================================================

    def import_data(
        self,
        data: Dict[str, Any]
    ) -> None:
        """
        Importa dados para o cache.
        """

        if not isinstance(
            data,
            dict
        ):

            return


        self.storage.update(
            data
        )



    # ==================================================
    # RESET COMPLETO
    # ==================================================

    def reset(
        self
    ) -> None:
        """
        Reinicia completamente
        o sistema de cache.
        """

        self.storage = {}



    # ==================================================
    # STATUS DO SERVIÇO
    # ==================================================

    def service_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações
        do serviço de cache.
        """

        return {

            "service":

                "cache",


            "module":

                "services.cache",


            "version":

                self.version,


            "initialized":

                True,


            "items":

                len(
                    self.storage
                ),


            "created_at":

                datetime.now()
                .isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO CACHE
# ======================================================

cache_manager = CacheManager()
