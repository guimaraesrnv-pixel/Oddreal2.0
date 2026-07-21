"""
OddReal 2.0

Módulo:
services/data_processor.py

Processador de dados recebidos.

Responsável por:
- Normalização
- Limpeza
- Padronização de eventos
- Preparação para análise

Versão: 2.0
"""


from typing import Dict, Any, List

from datetime import datetime



class DataProcessor:
    """
    Processador central de dados.
    """



    def __init__(self):

        self.version = "2.0"

        self.created_at = datetime.now()



    # ==================================================
    # VALIDAR DADOS RECEBIDOS
    # ==================================================

    def validate(
        self,
        data: Any
    ) -> bool:
        """
        Verifica se os dados possuem conteúdo.
        """

        if data is None:

            return False



        if isinstance(
            data,
            list
        ):

            return len(data) > 0



        if isinstance(
            data,
            dict
        ):

            return len(data) > 0



        return False



    # ==================================================
    # PROCESSAR RESPOSTA DA API
    # ==================================================

    def process_response(
        self,
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extrai dados úteis
        da resposta da API.
        """

        if not response.get(
            "success",
            False
        ):

            return []



        data = response.get(
            "data",
            []
        )


        if not self.validate(
            data
        ):

            return []



        return data
          # ==================================================
    # NORMALIZAR EVENTO
    # ==================================================

    def normalize_event(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converte evento bruto da API
        para o padrão interno.
        """

        return {

            "id":

                event.get(
                    "id",
                    ""
                ),


            "sport":

                event.get(
                    "sport_key",
                    ""
                ),


            "home_team":

                event.get(
                    "home_team",
                    ""
                ),


            "away_team":

                event.get(
                    "away_team",
                    ""
                ),


            "commence_time":

                event.get(
                    "commence_time",
                    ""
                ),


            "bookmakers":

                event.get(
                    "bookmakers",
                    []

                ),


            "processed_at":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # PROCESSAR EVENTOS EM LOTE
    # ==================================================

    def process_events(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normaliza uma lista de partidas.
        """

        processed = []


        for event in events:

            normalized = (
                self.normalize_event(
                    event
                )
            )


            processed.append(
                normalized
            )


        return processed



    # ==================================================
    # IDENTIFICAR TIMES
    # ==================================================

    def extract_teams(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Retorna os times da partida.
        """

        return {

            "home":

                event.get(
                    "home_team",
                    ""
                ),


            "away":

                event.get(
                    "away_team",
                    ""
                )

        }



    # ==================================================
    # IDENTIFICAR ESPORTE
    # ==================================================

    def extract_sport(
        self,
        event: Dict[str, Any]
    ) -> str:
        """
        Retorna esporte do evento.
        """

        return event.get(
            "sport",
            ""
        )



    # ==================================================
    # IDENTIFICAR ID DO EVENTO
    # ==================================================

    def extract_event_id(
        self,
        event: Dict[str, Any]
    ) -> str:
        """
        Retorna identificador único.
        """

        return event.get(
            "id",
            ""
        )
          # ==================================================
    # PROCESSAR BOOKMAKERS
    # ==================================================

    def process_bookmakers(
        self,
        bookmakers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normaliza casas de apostas
        recebidas da API.
        """

        processed = []


        for bookmaker in bookmakers:

            processed.append({

                "name":

                    bookmaker.get(
                        "title",
                        ""
                    ),


                "key":

                    bookmaker.get(
                        "key",
                        ""
                    ),


                "markets":

                    bookmaker.get(
                        "markets",
                        []

                    )

            })


        return processed



    # ==================================================
    # PROCESSAR MERCADOS
    # ==================================================

    def process_markets(
        self,
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normaliza mercados de apostas.
        """

        processed = []


        for market in markets:

            processed.append({

                "key":

                    market.get(
                        "key",
                        ""
                    ),


                "outcomes":

                    market.get(
                        "outcomes",
                        []

                    )

            })


        return processed



    # ==================================================
    # PROCESSAR ODDS
    # ==================================================

    def extract_odds(
        self,
        market: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extrai preços das odds.
        """

        odds = []


        outcomes = market.get(
            "outcomes",
            []
        )


        for outcome in outcomes:

            odds.append({

                "name":

                    outcome.get(
                        "name",
                        ""
                    ),


                "price":

                    outcome.get(
                        "price",
                        0

                    )

            })


        return odds



    # ==================================================
    # NORMALIZAR BOOKMAKERS DO EVENTO
    # ==================================================

    def normalize_bookmakers(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza bookmakers
        dentro do evento.
        """

        bookmakers = event.get(
            "bookmakers",
            []
        )


        return {

            "event_id":

                event.get(
                    "id",
                    ""
                ),


            "bookmakers":

                self.process_bookmakers(
                    bookmakers
                )

        }
          # ==================================================
    # COLETAR TODAS AS ODDS
    # ==================================================

    def collect_all_odds(
        self,
        bookmakers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reúne todas as odds disponíveis
        entre as casas.
        """

        collected = []


        for bookmaker in bookmakers:

            name = bookmaker.get(
                "name",
                ""
            )


            markets = bookmaker.get(
                "markets",
                []
            )


            for market in markets:

                outcomes = market.get(
                    "outcomes",
                    []
                )


                for outcome in outcomes:

                    collected.append({

                        "bookmaker":

                            name,


                        "market":

                            market.get(
                                "key",
                                ""
                            ),


                        "selection":

                            outcome.get(
                                "name",
                                ""
                            ),


                        "price":

                            outcome.get(
                                "price",
                                0

                            )

                    })


        return collected



    # ==================================================
    # CALCULAR MÉDIA DE ODDS
    # ==================================================

    def calculate_average_odds(
        self,
        odds: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calcula média das odds
        por seleção.
        """

        grouped = {}


        for item in odds:

            selection = item.get(
                "selection"
            )


            price = item.get(
                "price",
                0
            )


            if not selection or not price:

                continue



            if selection not in grouped:

                grouped[selection] = []



            grouped[selection].append(
                price
            )



        averages = {}


        for selection, values in grouped.items():

            averages[selection] = round(

                sum(values)
                /
                len(values),

                3

            )


        return averages



    # ==================================================
    # ENCONTRAR MELHOR ODDS
    # ==================================================

    def best_odds(
        self,
        odds: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Retorna a melhor cotação
        encontrada para cada seleção.
        """

        best = {}


        for item in odds:

            selection = item.get(
                "selection"
            )


            price = item.get(
                "price",
                0
            )


            if not selection:

                continue



            if (
                selection not in best
                or
                price > best[selection]["price"]
            ):

                best[selection] = item



        return best



    # ==================================================
    # CONSOLIDAR MERCADO
    # ==================================================

    def consolidate_market(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria visão consolidada
        de um mercado.
        """

        bookmakers = event.get(
            "bookmakers",
            []
        )


        odds = self.collect_all_odds(
            bookmakers
        )


        return {

            "event_id":

                event.get(
                    "id",
                    ""
                ),


            "total_quotes":

                len(
                    odds
                ),


            "average_odds":

                self.calculate_average_odds(
                    odds
                ),


            "best_odds":

                self.best_odds(
                    odds
                )

        }
         # ==================================================
    # PREPARAR ENTRADA PARA VALUE ENGINE
    # ==================================================

    def prepare_value_input(
        self,
        event: Dict[str, Any],
        market: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Converte dados processados
        para o formato esperado
        pelo ValueEngine.
        """

        opportunities = []


        best_odds = market.get(
            "best_odds",
            {}
        )


        average_odds = market.get(
            "average_odds",
            {}
        )


        for selection, odd_data in best_odds.items():

            opportunities.append({

                "event_id":

                    event.get(
                        "id",
                        ""
                    ),


                "sport":

                    event.get(
                        "sport",
                        ""
                    ),


                "home_team":

                    event.get(
                        "home_team",
                        ""
                    ),


                "away_team":

                    event.get(
                        "away_team",
                        ""
                    ),


                "selection":

                    selection,


                "odd":

                    odd_data.get(
                        "price",
                        0
                    ),


                "average_odd":

                    average_odds.get(
                        selection,
                        0
                    ),


                "bookmaker":

                    odd_data.get(
                        "bookmaker",
                        ""
                    )

            })


        return opportunities



    # ==================================================
    # CRIAR ESTRUTURA COMPLETA
    # ==================================================

    def build_analysis_package(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monta pacote completo
        para análise.
        """

        normalized_event = (
            self.normalize_event(
                event
            )
        )


        consolidated = (
            self.consolidate_market(
                normalized_event
            )
        )


        opportunities = (
            self.prepare_value_input(

                normalized_event,

                consolidated

            )
        )


        return {

            "event":

                normalized_event,


            "market":

                consolidated,


            "opportunities":

                opportunities,


            "created_at":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # PROCESSAR LISTA COMPLETA
    # ==================================================

    def build_batch_package(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processa vários eventos.
        """

        packages = []


        for event in events:

            packages.append(

                self.build_analysis_package(
                    event
                )

            )


        return packages
          # ==================================================
    # STATUS DO PROCESSADOR
    # ==================================================

    def service_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do serviço.
        """

        return {

            "service":

                "data_processor",


            "module":

                "services.data_processor",


            "version":

                self.version,


            "initialized":

                True,


            "created_at":

                self.created_at.isoformat()

        }



    # ==================================================
    # RESUMO DOS DADOS
    # ==================================================

    def data_summary(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gera resumo dos dados processados.
        """

        return {

            "total_items":

                len(
                    data
                ),


            "valid":

                self.validate(
                    data
                ),


            "generated_at":

                datetime.now()
                .isoformat()

        }



    # ==================================================
    # LIMPAR DADOS
    # ==================================================

    def clean(
        self,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove registros vazios
        ou inválidos.
        """

        cleaned = []


        for item in data:

            if isinstance(
                item,
                dict
            ) and len(item) > 0:

                cleaned.append(
                    item
                )


        return cleaned



    # ==================================================
    # PIPELINE COMPLETO
    # ==================================================

    def run(
        self,
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Executa processamento completo.
        """

        raw_data = (
            self.process_response(
                response
            )
        )


        cleaned = (
            self.clean(
                raw_data
            )
        )


        return self.process_events(
            cleaned
        )



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

data_processor = DataProcessor()
