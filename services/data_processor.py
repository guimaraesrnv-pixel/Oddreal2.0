"""
OddReal 2.0

Módulo:
services/data_processor.py

Processador de dados recebidos.

Responsável por:
- Validação;
- Limpeza;
- Normalização;
- Padronização de eventos;
- Padronização de bookmakers;
- Preparação para análise;
- Consolidação das odds;
- Preparação para o ValueBetEngine.

IMPORTANTE:
- Não consulta a API.
- Não contém API Key.
- Não calcula Value Bet.
- Não substitui o OddsEngine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class DataProcessor:
    """
    Processador central de dados do OddReal.
    """

    def __init__(self) -> None:

        self.version = "2.0"

        self.created_at = (
            datetime.now(
                timezone.utc
            )
        )

    # ==========================================================
    # TIMESTAMP
    # ==========================================================

    @staticmethod
    def _now_iso() -> str:
        """
        Retorna timestamp UTC.
        """

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )

    # ==========================================================
    # CONVERSÃO SEGURA
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Converte um valor para float.
        """

        try:

            result = float(
                value
            )

            if result != result:

                return default

            return result

        except (
            TypeError,
            ValueError,
        ):

            return default

    # ==========================================================
    # VALIDAR DADOS
    # ==========================================================

    def validate(
        self,
        data: Any,
    ) -> bool:
        """
        Verifica se os dados possuem estrutura válida.
        """

        if data is None:

            return False

        if isinstance(
            data,
            list,
        ):

            return len(data) > 0

        if isinstance(
            data,
            dict,
        ):

            return len(data) > 0

        return False

    # ==========================================================
    # PROCESSAR RESPOSTA
    # ==========================================================

    def process_response(
        self,
        response: Any,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Extrai os eventos de uma resposta.

        Aceita:
        - lista direta de eventos;
        - {"success": True, "data": [...]};
        - {"data": [...]};
        """

        # ------------------------------------------------------
        # LISTA DIRETA
        # ------------------------------------------------------

        if isinstance(
            response,
            list,
        ):

            return [

                item

                for item in response

                if isinstance(
                    item,
                    dict,
                )

            ]

        # ------------------------------------------------------
        # DICIONÁRIO
        # ------------------------------------------------------

        if not isinstance(
            response,
            dict,
        ):

            return []

        # ------------------------------------------------------
        # RESPOSTA PADRONIZADA
        # ------------------------------------------------------

        if (
            "success" in response
            and not response.get(
                "success",
                False,
            )
        ):

            return []

        data = response.get(
            "data",
            response,
        )

        if not isinstance(
            data,
            list,
        ):

            return []

        return [

            item

            for item in data

            if isinstance(
                item,
                dict,
            )

        ]

    # ==========================================================
    # NORMALIZAR EVENTO
    # ==========================================================

    def normalize_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normaliza um evento da The Odds API.

        A estrutura de bookmakers permanece compatível
        com o formato original da API.
        """

        if not isinstance(
            event,
            dict,
        ):

            return {}

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            bookmakers = []

        normalized_bookmakers = (
            self.process_bookmakers(
                bookmakers
            )
        )

        return {

            "id":
                str(
                    event.get(
                        "id",
                        "",
                    )
                ).strip(),

            "sport_key":
                str(
                    event.get(
                        "sport_key",
                        "",
                    )
                ).strip(),

            "sport_title":
                str(
                    event.get(
                        "sport_title",
                        event.get(
                            "sport_key",
                            "",
                        ),
                    )
                ).strip(),

            "home_team":
                str(
                    event.get(
                        "home_team",
                        "",
                    )
                ).strip(),

            "away_team":
                str(
                    event.get(
                        "away_team",
                        "",
                    )
                ).strip(),

            "commence_time":
                str(
                    event.get(
                        "commence_time",
                        "",
                    )
                ).strip(),

            "bookmakers":
                normalized_bookmakers,

            "processed_at":
                self._now_iso(),

        }

    # ==========================================================
    # PROCESSAR EVENTOS
    # ==========================================================

    def process_events(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Normaliza uma lista de eventos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        processed: List[
            Dict[str, Any]
        ] = []

        for event in events:

            if not isinstance(
                event,
                dict,
            ):

                continue

            normalized = (
                self.normalize_event(
                    event
                )
            )

            if not normalized.get(
                "id"
            ):

                continue

            if not normalized.get(
                "home_team"
            ):

                continue

            if not normalized.get(
                "away_team"
            ):

                continue

            processed.append(
                normalized
            )

        return processed

    # ==========================================================
    # TIMES
    # ==========================================================

    def extract_teams(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Retorna os times da partida.
        """

        return {

            "home":
                str(
                    event.get(
                        "home_team",
                        "",
                    )
                ).strip(),

            "away":
                str(
                    event.get(
                        "away_team",
                        "",
                    )
                ).strip(),

        }

    # ==========================================================
    # ESPORTE
    # ==========================================================

    def extract_sport(
        self,
        event: Dict[str, Any],
    ) -> str:
        """
        Retorna o esporte.
        """

        return str(
            event.get(
                "sport_key",
                event.get(
                    "sport",
                    "",
                ),
            )
        ).strip()

    # ==========================================================
    # ID
    # ==========================================================

    def extract_event_id(
        self,
        event: Dict[str, Any],
    ) -> str:
        """
        Retorna o ID do evento.
        """

        return str(
            event.get(
                "id",
                "",
            )
        ).strip()

    # ==========================================================
    # BOOKMAKERS
    # ==========================================================

    def process_bookmakers(
        self,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Normaliza bookmakers sem destruir
        a estrutura necessária pelo Analyzer.
        """

        if not isinstance(
            bookmakers,
            list,
        ):

            return []

        processed: List[
            Dict[str, Any]
        ] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            title = str(
                bookmaker.get(
                    "title",
                    "",
                )
            ).strip()

            key = str(
                bookmaker.get(
                    "key",
                    "",
                )
            ).strip()

            markets = (
                self.process_markets(
                    bookmaker.get(
                        "markets",
                        [],
                    )
                )
            )

            if not markets:

                continue

            processed.append(
                {

                    "title": title,

                    "key": key,

                    "markets": markets,

                }
            )

        return processed

    # ==========================================================
    # MERCADOS
    # ==========================================================

    def process_markets(
        self,
        markets: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Normaliza mercados e outcomes.
        """

        if not isinstance(
            markets,
            list,
        ):

            return []

        processed: List[
            Dict[str, Any]
        ] = []

        for market in markets:

            if not isinstance(
                market,
                dict,
            ):

                continue

            key = str(
                market.get(
                    "key",
                    "",
                )
            ).strip()

            outcomes = (
                market.get(
                    "outcomes",
                    [],
                )
            )

            if not isinstance(
                outcomes,
                list,
            ):

                outcomes = []

            processed_outcomes: List[
                Dict[str, Any]
            ] = []

            for outcome in outcomes:

                if not isinstance(
                    outcome,
                    dict,
                ):

                    continue

                name = str(
                    outcome.get(
                        "name",
                        "",
                    )
                ).strip()

                price = self._safe_float(
                    outcome.get(
                        "price",
                        0,
                    )
                )

                if not name:

                    continue

                if price <= 0:

                    continue

                item = {

                    "name": name,

                    "price": price,

                }

                # Mantém pontos extras quando
                # existirem na resposta da API.

                if (
                    "point"
                    in outcome
                ):

                    item["point"] = (
                        outcome.get(
                            "point"
                        )
                    )

                processed_outcomes.append(
                    item
                )

            if not processed_outcomes:

                continue

            processed.append(
                {

                    "key": key,

                    "outcomes":
                        processed_outcomes,

                }
            )

        return processed

    # ==========================================================
    # ODDS
    # ==========================================================

    def extract_odds(
        self,
        market: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Extrai todas as odds de um mercado.
        """

        if not isinstance(
            market,
            dict,
        ):

            return []

        odds: List[
            Dict[str, Any]
        ] = []

        outcomes = market.get(
            "outcomes",
            [],
        )

        if not isinstance(
            outcomes,
            list,
        ):

            return []

        for outcome in outcomes:

            if not isinstance(
                outcome,
                dict,
            ):

                continue

            name = str(
                outcome.get(
                    "name",
                    "",
                )
            ).strip()

            price = self._safe_float(
                outcome.get(
                    "price",
                    0,
                )
            )

            if not name or price <= 0:

                continue

            odds.append(
                {

                    "name": name,

                    "price": price,

                }
            )

        return odds

    # ==========================================================
    # NORMALIZAR BOOKMAKERS DO EVENTO
    # ==========================================================

    def normalize_bookmakers(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Retorna bookmakers normalizados.
        """

        if not isinstance(
            event,
            dict,
        ):

            return {

                "event_id": "",

                "bookmakers": [],

            }

        return {

            "event_id":
                event.get(
                    "id",
                    "",
                ),

            "bookmakers":
                self.process_bookmakers(
                    event.get(
                        "bookmakers",
                        [],
                    )
                ),

        }

    # ==========================================================
    # COLETAR TODAS AS ODDS
    # ==========================================================

    def collect_all_odds(
        self,
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Reúne todas as cotações.
        """

        if not isinstance(
            bookmakers,
            list,
        ):

            return []

        collected: List[
            Dict[str, Any]
        ] = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):

                continue

            bookmaker_name = (
                bookmaker.get(
                    "title",
                    bookmaker.get(
                        "name",
                        bookmaker.get(
                            "key",
                            "",
                        ),
                    ),
                )
            )

            markets = bookmaker.get(
                "markets",
                [],
            )

            if not isinstance(
                markets,
                list,
            ):

                continue

            for market in markets:

                if not isinstance(
                    market,
                    dict,
                ):

                    continue

                market_key = (
                    market.get(
                        "key",
                        "",
                    )
                )

                for outcome in market.get(
                    "outcomes",
                    [],
                ):

                    if not isinstance(
                        outcome,
                        dict,
                    ):

                        continue

                    price = self._safe_float(
                        outcome.get(
                            "price",
                            0,
                        )
                    )

                    if price <= 0:

                        continue

                    collected.append(
                        {

                            "bookmaker":
                                bookmaker_name,

                            "market":
                                market_key,

                            "selection":
                                outcome.get(
                                    "name",
                                    "",
                                ),

                            "price":
                                price,

                        }
                    )

        return collected

    # ==========================================================
    # MÉDIA DAS ODDS
    # ==========================================================

    def calculate_average_odds(
        self,
        odds: List[
            Dict[str, Any]
        ],
    ) -> Dict[
        str,
        float
    ]:
        """
        Calcula a média por seleção.
        """

        grouped: Dict[
            str,
            List[float]
        ] = {}

        for item in odds:

            if not isinstance(
                item,
                dict,
            ):

                continue

            selection = str(
                item.get(
                    "selection",
                    "",
                )
            ).strip()

            price = self._safe_float(
                item.get(
                    "price",
                    0,
                )
            )

            if not selection or price <= 0:

                continue

            grouped.setdefault(
                selection,
                [],
            ).append(
                price
            )

        return {

            selection:
                round(
                    sum(values)
                    / len(values),
                    3,
                )

            for selection, values
            in grouped.items()

            if values

        }

    # ==========================================================
    # MELHORES ODDS
    # ==========================================================

    def best_odds(
        self,
        odds: List[
            Dict[str, Any]
        ],
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:
        """
        Retorna a maior odd por seleção.
        """

        best: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for item in odds:

            if not isinstance(
                item,
                dict,
            ):

                continue

            selection = str(
                item.get(
                    "selection",
                    "",
                )
            ).strip()

            price = self._safe_float(
                item.get(
                    "price",
                    0,
                )
            )

            if not selection or price <= 0:

                continue

            if (
                selection not in best
                or price
                > self._safe_float(
                    best[
                        selection
                    ].get(
                        "price",
                        0,
                    )
                )
            ):

                best[selection] = dict(
                    item
                )

        return best

    # ==========================================================
    # CONSOLIDAR MERCADO
    # ==========================================================

    def consolidate_market(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Cria visão consolidada das odds.
        """

        if not isinstance(
            event,
            dict,
        ):

            return {

                "event_id": "",

                "total_quotes": 0,

                "average_odds": {},

                "best_odds": {},

            }

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        odds = (
            self.collect_all_odds(
                bookmakers
            )
        )

        return {

            "event_id":
                event.get(
                    "id",
                    "",
                ),

            "total_quotes":
                len(odds),

            "average_odds":
                self.calculate_average_odds(
                    odds
                ),

            "best_odds":
                self.best_odds(
                    odds
                ),

        }

    # ==========================================================
    # PREPARAR VALUE ENGINE
    # ==========================================================

    def prepare_value_input(
        self,
        event: Dict[str, Any],
        market: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Prepara oportunidades para o ValueBetEngine.
        """

        if not isinstance(
            event,
            dict,
        ):

            return []

        if not isinstance(
            market,
            dict,
        ):

            return []

        opportunities: List[
            Dict[str, Any]
        ] = []

        best = market.get(
            "best_odds",
            {},
        )

        averages = market.get(
            "average_odds",
            {},
        )

        if not isinstance(
            best,
            dict,
        ):

            best = {}

        if not isinstance(
            averages,
            dict,
        ):

            averages = {}

        for selection, odd_data in best.items():

            if not isinstance(
                odd_data,
                dict,
            ):

                continue

            opportunities.append(
                {

                    "event_id":
                        event.get(
                            "id",
                            "",
                        ),

                    "sport":
                        event.get(
                            "sport_title",
                            event.get(
                                "sport_key",
                                "",
                            ),
                        ),

                    "home_team":
                        event.get(
                            "home_team",
                            "",
                        ),

                    "away_team":
                        event.get(
                            "away_team",
                            "",
                        ),

                    "selection":
                        selection,

                    "odd":
                        self._safe_float(
                            odd_data.get(
                                "price",
                                0,
                            )
                        ),

                    "average_odd":
                        self._safe_float(
                            averages.get(
                                selection,
                                0,
                            )
                        ),

                    "bookmaker":
                        odd_data.get(
                            "bookmaker",
                            odd_data.get(
                                "title",
                                "",
                            ),
                        ),

                    "market":
                        odd_data.get(
                            "market",
                            "",
                        ),

                }
            )

        return opportunities

    # ==========================================================
    # PACOTE DE ANÁLISE
    # ==========================================================

    def build_analysis_package(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Cria pacote completo de análise.
        """

        normalized = (
            self.normalize_event(
                event
            )
        )

        if not normalized:

            return {}

        consolidated = (
            self.consolidate_market(
                normalized
            )
        )

        opportunities = (
            self.prepare_value_input(
                normalized,
                consolidated,
            )
        )

        return {

            "event":
                normalized,

            "market":
                consolidated,

            "opportunities":
                opportunities,

            "created_at":
                self._now_iso(),

        }

    # ==========================================================
    # LOTE
    # ==========================================================

    def build_batch_package(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Cria pacotes para vários eventos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        packages: List[
            Dict[str, Any]
        ] = []

        for event in events:

            package = (
                self.build_analysis_package(
                    event
                )
            )

            if package:

                packages.append(
                    package
                )

        return packages

    # ==========================================================
    # STATUS
    # ==========================================================

    def service_status(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna status do processador.
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
                self.created_at.isoformat(),

        }

    # ==========================================================
    # RESUMO
    # ==========================================================

    def data_summary(
        self,
        data: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Gera resumo dos dados.
        """

        if not isinstance(
            data,
            list,
        ):

            data = []

        valid = [

            item

            for item in data

            if isinstance(
                item,
                dict,
            )
            and bool(item)

        ]

        sports = sorted(
            {
                str(
                    item.get(
                        "sport_title",
                        item.get(
                            "sport_key",
                            "",
                        ),
                    )
                )

                for item in valid

                if item.get(
                    "sport_title",
                    item.get(
                        "sport_key",
                        "",
                    ),
                )
            }
        )

        return {

            "total_items":
                len(data),

            "valid_items":
                len(valid),

            "total_sports":
                len(sports),

            "sports":
                sports,

            "valid":
                len(valid) > 0,

            "generated_at":
                self._now_iso(),

        }

    # ==========================================================
    # LIMPEZA
    # ==========================================================

    def clean(
        self,
        data: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Remove registros inválidos.
        """

        if not isinstance(
            data,
            list,
        ):

            return []

        return [

            item

            for item in data

            if isinstance(
                item,
                dict,
            )
            and bool(item)

        ]

    # ==========================================================
    # PIPELINE LOCAL
    # ==========================================================

    def run(
        self,
        response: Any,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Executa o processamento completo.
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


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

data_processor = DataProcessor()
