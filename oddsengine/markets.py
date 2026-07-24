"""
OddReal 2.0
Módulo: oddsengine/markets.py

Gerenciador de mercados de apostas.

Responsável por:
- Classificação de mercados
- Padronização
- Organização dos tipos de aposta
- Preparação para análise

Versão: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime


class MarketManager:
    """
    Motor de gerenciamento de mercados.
    """


    def __init__(self):

        self.version = "2.0"

        self.created_at = datetime.now()


        self.market_types = [

            "moneyline",

            "draw",

            "over_under",

            "btts",

            "handicap",

            "corners",

            "cards",

            "player_props"

        ]



    # ==================================================
    # VALIDAÇÃO DE MERCADO
    # ==================================================

    def validate_market(
        self,
        market: Dict[str, Any]
    ) -> bool:
        """
        Verifica se o mercado
        possui estrutura válida.
        """

        if not market:

            return False


        if "outcomes" not in market:

            return False


        return True



    # ==================================================
    # CLASSIFICAÇÃO DO MERCADO
    # ==================================================

    def classify_market(
        self,
        market_name: str
    ) -> str:
        """
        Identifica categoria do mercado.
        """

        name = (
            market_name
            .lower()
        )


        if (
            "h2h" in name
            or
            "winner" in name
        ):

            return "moneyline"



        elif (
            "totals" in name
            or
            "over" in name
        ):

            return "over_under"



        elif (
            "both" in name
            or
            "btts" in name
        ):

            return "btts"



        elif (
            "spread" in name
            or
            "handicap" in name
        ):

            return "handicap"



        elif (
            "corner" in name
        ):

            return "corners"



        elif (
            "card" in name
        ):

            return "cards"



        else:

            return "unknown"



    # ==================================================
    # NORMALIZAÇÃO DE MERCADO
    # ==================================================

    def normalize_market(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converte mercado recebido
        para padrão interno.
        """

        market_name = market.get(
            "key",
            market.get(
                "market",
                ""
            )
        )


        return {

            "name":
                market_name,


            "type":
                self.classify_market(
                    market_name
                ),


            "outcomes":
                market.get(
                    "outcomes",
                    []
                ),


            "updated_at":
                datetime.now().isoformat()

        }
          # ==================================================
    # EXTRAÇÃO DE SELEÇÕES
    # ==================================================

    def extract_outcomes(
        self,
        market: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extrai seleções disponíveis
        em um mercado.
        """

        outcomes = []


        for item in market.get(
            "outcomes",
            []
        ):

            outcomes.append(

                {

                    "name":
                        item.get(
                            "name",
                            ""
                        ),


                    "price":
                        item.get(
                            "price",
                            0
                        ),


                    "point":
                        item.get(
                            "point",
                            None
                        )

                }

            )


        return outcomes



    # ==================================================
    # CRIAÇÃO DE MERCADO INTERNO
    # ==================================================

    def create_market_object(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria estrutura padrão interna
        para qualquer mercado.
        """

        normalized = (
            self.normalize_market(
                market
            )
        )


        outcomes = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "market":
                normalized["name"],


            "category":
                normalized["type"],


            "selections":
                outcomes,


            "active":
                True,


            "created_at":
                datetime.now().isoformat()

        }



    # ==================================================
    # SEPARAÇÃO POR CATEGORIA
    # ==================================================

    def group_by_category(
        self,
        markets: List[Dict[str, Any]]
    ) -> Dict[str, List]:
        """
        Organiza mercados por tipo.
        """

        grouped = {}


        for market in markets:

            category = market.get(
                "category",
                "unknown"
            )


            if category not in grouped:

                grouped[category] = []



            grouped[category].append(
                market
            )



        return grouped



    # ==================================================
    # BUSCAR MERCADOS POR TIPO
    # ==================================================

    def get_markets_by_type(
        self,
        markets: List[Dict[str, Any]],
        market_type: str
    ) -> List[Dict[str, Any]]:
        """
        Retorna apenas mercados
        de uma categoria específica.
        """

        result = []


        for market in markets:

            if (
                market.get(
                    "category"
                )
                ==
                market_type
            ):

                result.append(
                    market
                )


        return result



    # ==================================================
    # CONTAGEM DE MERCADOS
    # ==================================================

    def market_statistics(
        self,
        markets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Estatísticas gerais
        dos mercados recebidos.
        """

        categories = (
            self.group_by_category(
                markets
            )
        )


        return {

            "total_markets":
                len(
                    markets
                ),


            "categories":
                {

                    key:
                        len(value)

                    for key, value
                    in categories.items()

                }

        }
          # ==================================================
    # FILTRO DE MERCADOS PERMITIDOS
    # ==================================================

    def filter_supported_markets(
        self,
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove mercados desconhecidos
        e mantém apenas os suportados.
        """

        supported = []


        for market in markets:

            category = market.get(
                "category",
                "unknown"
            )


            if category in self.market_types:

                supported.append(
                    market
                )


        return supported



    # ==================================================
    # FILTRO POR QUALIDADE DE MERCADO
    # ==================================================

    def filter_quality_markets(
        self,
        markets: List[Dict[str, Any]],
        minimum_outcomes: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Remove mercados sem liquidez
        ou sem seleções suficientes.
        """

        result = []


        for market in markets:

            selections = market.get(
                "selections",
                []
            )


            if len(selections) >= minimum_outcomes:

                result.append(
                    market
                )


        return result



    # ==================================================
    # PREPARAÇÃO PARA ANÁLISE DE VALOR
    # ==================================================

    def prepare_for_analysis(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara mercado para o OddsEngine.
        """

        selections = []


        for item in market.get(
            "selections",
            []
        ):

            selections.append(

                {

                    "name":
                        item.get(
                            "name",
                            ""
                        ),


                    "odd":
                        item.get(
                            "price",
                            0
                        ),


                    "line":
                        item.get(
                            "point",
                            None
                        )

                }

            )


        return {

            "market":
                market.get(
                    "market",
                    ""
                ),


            "type":
                market.get(
                    "category",
                    ""
                ),


            "selections":
                selections

        }



    # ==================================================
    # PREPARAR VÁRIOS MERCADOS
    # ==================================================

    def prepare_markets_batch(
        self,
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepara uma lista completa
        para análise matemática.
        """

        prepared = []


        for market in markets:

            prepared.append(

                self.prepare_for_analysis(
                    market
                )

            )


        return prepared



    # ==================================================
    # BUSCA DO MERCADO PRINCIPAL
    # ==================================================

    def find_main_market(
        self,
        markets: List[Dict[str, Any]],
        market_type: str
    ) -> Dict[str, Any]:
        """
        Retorna o primeiro mercado
        encontrado de determinada categoria.
        """

        for market in markets:

            if (
                market.get(
                    "category"
                )
                ==
                market_type
            ):

                return market



        return {}
          # ==================================================
    # MERCADO 1X2
    # ==================================================

    def parse_moneyline(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercado vencedor da partida.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "type":
                "moneyline",

            "home":
                selections[0]
                if len(selections) > 0
                else {},

            "away":
                selections[1]
                if len(selections) > 1
                else {},

            "draw":
                selections[2]
                if len(selections) > 2
                else {}

        }



    # ==================================================
    # MERCADO OVER / UNDER
    # ==================================================

    def parse_over_under(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza linhas de gols.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        result = {

            "type":
                "over_under",

            "lines":
                []

        }


        for item in selections:

            result["lines"].append(

                {

                    "name":
                        item["name"],

                    "line":
                        item["point"],

                    "odd":
                        item["price"]

                }

            )


        return result



    # ==================================================
    # MERCADO AMBAS MARCAM
    # ==================================================

    def parse_btts(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercado BTTS.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        result = {

            "type":
                "btts",

            "yes":
                {},

            "no":
                {}

        }


        for item in selections:

            name = (
                item["name"]
                .lower()
            )


            if (
                "yes" in name
                or
                "sim" in name
            ):

                result["yes"] = item


            elif (
                "no" in name
                or
                "não" in name
            ):

                result["no"] = item



        return result



    # ==================================================
    # MERCADO HANDICAP
    # ==================================================

    def parse_handicap(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercados handicap.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "type":
                "handicap",

            "selections":
                selections

        }



    # ==================================================
    # CONVERSOR AUTOMÁTICO
    # ==================================================

    def parse_market(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Escolhe automaticamente
        o interpretador correto.
        """

        category = market.get(
            "category",
            ""
        )


        if category == "moneyline":

            return self.parse_moneyline(
                market
            )


        elif category == "over_under":

            return self.parse_over_under(
                market
            )


        elif category == "btts":

            return self.parse_btts(
                market
            )


        elif category == "handicap":

            return self.parse_handicap(
                market
            )



        return market
          # ==================================================
    # MERCADO DE ESCANTEIOS
    # ==================================================

    def parse_corners(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercados de escanteios.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "type":
                "corners",

            "lines":
                selections

        }



    # ==================================================
    # MERCADO DE CARTÕES
    # ==================================================

    def parse_cards(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercados de cartões.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "type":
                "cards",

            "lines":
                selections

        }



    # ==================================================
    # MERCADO DE JOGADORES
    # ==================================================

    def parse_player_props(
        self,
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organiza mercados individuais
        de jogadores.
        """

        selections = (
            self.extract_outcomes(
                market
            )
        )


        return {

            "type":
                "player_props",

            "players":
                selections

        }



    # ==================================================
    # FILTRO POR ESPORTE
    # ==================================================

    def filter_by_sport(
        self,
        markets: List[Dict[str, Any]],
        sport: str
    ) -> List[Dict[str, Any]]:
        """
        Filtra mercados por esporte.
        """

        filtered = []


        for market in markets:

            if (
                market
                .get(
                    "sport",
                    ""
                )
                .lower()
                ==
                sport.lower()
            ):

                filtered.append(
                    market
                )


        return filtered



    # ==================================================
    # FILTRO POR CASA DE APOSTAS
    # ==================================================

    def filter_by_bookmaker(
        self,
        markets: List[Dict[str, Any]],
        bookmaker: str
    ) -> List[Dict[str, Any]]:
        """
        Retorna mercados de uma casa específica.
        """

        filtered = []


        for market in markets:

            if (
                market
                .get(
                    "bookmaker",
                    ""
                )
                .lower()
                ==
                bookmaker.lower()
            ):

                filtered.append(
                    market
                )


        return filtered



    # ==================================================
    # PROCESSADOR COMPLETO
    # ==================================================

    def process_markets(
        self,
        raw_markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Pipeline completo:

        Recebe mercados crus
        Normaliza
        Filtra
        Converte
        """

        processed = []


        for market in raw_markets:

            if not self.validate_market(
                market
            ):

                continue



            normalized = (
                self.create_market_object(
                    market
                )
            )


            processed.append(
                normalized
            )



        processed = (
            self.filter_supported_markets(
                processed
            )
        )


        processed = (
            self.filter_quality_markets(
                processed
            )
        )


        return processed
          # ==================================================
    # RELATÓRIO DE MERCADOS
    # ==================================================

    def generate_market_report(
        self,
        markets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gera relatório geral dos mercados.
        """

        statistics = (
            self.market_statistics(
                markets
            )
        )


        grouped = (
            self.group_by_category(
                markets
            )
        )


        return {

            "total_markets":

                statistics
                .get(
                    "total_markets",
                    0
                ),


            "categories":

                statistics
                .get(
                    "categories",
                    {}
                ),


            "available_types":

                list(
                    grouped.keys()
                ),


            "generated_at":

                datetime.now().isoformat()

        }



    # ==================================================
    # BUSCA DE MELHORES MERCADOS
    # ==================================================

    def select_priority_markets(
        self,
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Seleciona mercados prioritários
        para análise do OddReal.

        Prioridade:
        1X2
        Over/Under
        BTTS
        Handicap
        """

        priority = [

            "moneyline",

            "over_under",

            "btts",

            "handicap"

        ]


        selected = []


        for market in markets:

            if (
                market
                .get(
                    "category"
                )
                in priority
            ):

                selected.append(
                    market
                )


        return selected



    # ==================================================
    # PREPARAÇÃO PARA ODDS ENGINE
    # ==================================================

    def export_to_odds_engine(
        self,
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Formata mercados para consumo
        pelo OddsEngine.
        """

        exported = []


        for market in markets:

            exported.append(

                {

                    "market":
                        market.get(
                            "market",
                            ""
                        ),


                    "type":
                        market.get(
                            "category",
                            ""
                        ),


                    "selections":

                        [

                            {

                                "name":
                                    item.get(
                                        "name",
                                        ""
                                    ),


                                "odd":
                                    item.get(
                                        "price",
                                        0
                                    ),


                                "line":
                                    item.get(
                                        "point",
                                        None
                                    )

                            }

                            for item
                            in market.get(
                                "selections",
                                []
                            )

                        ]

                }

            )


        return exported



    # ==================================================
    # STATUS DO MOTOR
    # ==================================================

    def engine_status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do módulo.
        """

        return {

            "module":
                "oddsengine.markets",


            "class":
                "MarketManager",


            "version":
                self.version,


            "initialized":
                True,


            "created_at":
                self.created_at.isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL DO GERENCIADOR
# ======================================================

market_manager = MarketManager()
