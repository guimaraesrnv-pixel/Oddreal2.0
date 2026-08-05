"""
OddReal 2.0
Analyzer

Responsável por:

- analisar eventos recebidos da The Odds API;
- consolidar odds por mercado e seleção;
- calcular probabilidade de mercado;
- remover o overround/margem das casas;
- calcular EV matematicamente;
- calcular o Índice OddReal;
- classificar risco;
- identificar Value Bets;
- identificar melhor oportunidade;
- fornecer resumo estatístico.

IMPORTANTE:
Este módulo NÃO coleta dados da API.
Este módulo NÃO altera os bookmakers originais.
Este módulo NÃO depende da interface Streamlit.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.logger import info, error
from oddsengine.value import valuebet_engine


class Analyzer:
    """
    Motor central de análise quantitativa do OddReal 2.0.
    """

    # ==========================================================
    # CONFIGURAÇÕES
    # ==========================================================

    # EV mínimo para considerar Value Bet.
    VALUE_BET_MIN_EV = 5.0

    # Índice mínimo para uma oportunidade ser considerada
    # realmente interessante.
    MIN_OPPORTUNITY_INDEX = 50.0

    # Mercados considerados prioritários.
    PRIMARY_MARKETS = {
        "h2h",
        "totals",
        "spreads",
    }

    def __init__(self) -> None:

        info(
            "Analyzer OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float:
        """
        Conversão segura para float.

        Retorna 0.0 quando o valor é inválido.
        """

        try:

            if value is None:
                return 0.0

            result = float(value)

            if result <= 0:
                return 0.0

            return result

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

    # ==========================================================
    # PROBABILIDADE IMPLÍCITA
    # ==========================================================

    def implied_probability(
        self,
        odd: float,
    ) -> float:
        """
        Converte odd decimal em probabilidade implícita.

        Exemplo:

            odd = 2.00

            probabilidade = 1 / 2
            = 50%

        Retorna percentual de 0 a 100.
        """

        odd = self._safe_float(
            odd
        )

        if odd <= 1.0:
            return 0.0

        return round(
            (1.0 / odd) * 100.0,
            4,
        )

    # ==========================================================
    # PROBABILIDADE DE MERCADO
    # ==========================================================

    def _market_probabilities(
        self,
        outcomes: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Calcula probabilidades implícitas de todas as seleções
        e remove o overround da casa.

        Exemplo:

            odds:
                2.00
                3.00
                4.00

        Primeiro calculamos:

            50%
            33.33%
            25%

        Soma:

            108.33%

        Depois normalizamos:

            50 / 108.33
            33.33 / 108.33
            25 / 108.33

        O resultado representa uma probabilidade de mercado
        normalizada, sem a margem matemática da casa.
        """

        raw: Dict[str, float] = {}

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

            odd = self._safe_float(
                outcome.get(
                    "odd"
                )
            )

            if not name or odd <= 1.0:
                continue

            probability = (
                self.implied_probability(
                    odd
                )
            )

            if probability > 0:

                raw[name] = (
                    raw.get(
                        name,
                        0.0,
                    )
                    + probability
                )

        total = sum(
            raw.values()
        )

        if total <= 0:
            return {}

        normalized: Dict[
            str,
            float
        ] = {}

        for name, probability in raw.items():

            normalized[name] = round(
                (
                    probability
                    / total
                )
                * 100.0,
                4,
            )

        return normalized

    # ==========================================================
    # EV
    # ==========================================================

    def expected_value(
        self,
        probability: float,
        odd: float,
    ) -> float:
        """
        Calcula o Expected Value percentual.

        probability:
            Probabilidade justa em escala 0-100.

        odd:
            Odd decimal.

        Fórmula:

            EV = (P × odd - 1) × 100

        onde P é convertido de percentual para decimal.

        Exemplo:

            probability = 15
            odd = 8

            P = 0.15

            EV = (0.15 × 8 - 1) × 100

            EV = 20%

        IMPORTANTE:
        Não existe Value Bet simplesmente porque a odd é alta.

        A odd precisa ser comparada com uma probabilidade
        matematicamente estimada.
        """

        probability = self._safe_float(
            probability
        )

        odd = self._safe_float(
            odd
        )

        if (
            probability <= 0
            or odd <= 1.0
        ):
            return 0.0

        probability_decimal = (
            probability / 100.0
        )

        return round(
            (
                probability_decimal
                * odd
                - 1.0
            )
            * 100.0,
            4,
        )

    # ==========================================================
    # VALIDAÇÃO DO EV
    # ==========================================================

    def _is_value_bet(
        self,
        expected_value: float,
    ) -> bool:
        """
        Determina se uma análise é Value Bet.

        O critério quantitativo principal é:

            EV >= 5%

        EV negativo jamais é Value Bet.
        """

        try:

            return (
                float(expected_value)
                >= self.VALUE_BET_MIN_EV
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

    # ==========================================================
    # RISCO
    # ==========================================================

    def _risk_level(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:
        """
        Classifica risco.

        O risco NÃO determina se existe Value Bet.

        EV e risco são conceitos diferentes.
        """

        odd = self._safe_float(
            odd
        )

        probability = self._safe_float(
            probability
        )

        index = self._safe_float(
            index
        )

        # Odds extremamente altas são naturalmente
        # mais voláteis.
        if odd >= 8.0:
            return "Alto"

        if odd >= 5.0:
            return "Alto"

        if probability < 15.0:
            return "Alto"

        if index < 40.0:
            return "Alto"

        if index < 65.0:
            return "Moderado"

        return "Baixo"

    # Compatibilidade com versões anteriores.
    def _risk(
        self,
        odd: float,
        probability: float,
        index: float,
    ) -> str:
        return self._risk_level(
            odd,
            probability,
            index,
        )

    # ==========================================================
    # CONFIANÇA
    # ==========================================================

    def _confidence_level(
        self,
        index: float,
    ) -> str:
        """
        Classifica confiança exclusivamente pelo índice.
        """

        index = self._safe_float(
            index
        )

        if index >= 70:
            return "Alta"

        if index >= 45:
            return "Moderada"

        return "Baixa"

    # ==========================================================
    # ÍNDICE ODdREAL
    # ==========================================================

    def _calculate_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int,
    ) -> float:
        """
        Calcula o Índice OddReal.

        O índice NÃO é o EV.

        Componentes:

        1. Probabilidade estimada;
        2. EV;
        3. quantidade de casas disponíveis.

        O objetivo é evitar que uma odd isolada produza
        automaticamente um índice absurdo.

        O resultado fica entre 0 e 100.
        """

        probability = max(
            0.0,
            min(
                100.0,
                self._safe_float(
                    probability
                ),
            ),
        )

        expected_value = self._safe_float(
            expected_value
        )

        market_count = max(
            0,
            int(
                market_count
            ),
        )

        # ------------------------------------------------------
        # COMPONENTE DE PROBABILIDADE
        # ------------------------------------------------------

        probability_score = min(
            60.0,
            probability * 0.60,
        )

        # ------------------------------------------------------
        # COMPONENTE DE EV
        # ------------------------------------------------------

        # EV positivo ajuda o índice.
        # EV negativo não destrói completamente o índice,
        # mas não gera bônus.
        ev_score = max(
            0.0,
            min(
                30.0,
                expected_value * 1.5,
            ),
        )

        # ------------------------------------------------------
        # COMPONENTE DE MERCADO
        # ------------------------------------------------------

        # Mais casas = maior robustez da análise.
        market_score = min(
            10.0,
            market_count * 2.0,
        )

        index = (
            probability_score
            + ev_score
            + market_score
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    index,
                ),
            ),
            2,
        )

    # Compatibilidade com versões anteriores.
    def _oddreal_index(
        self,
        probability: float,
        odd: float,
        expected_value: float,
        market_count: int = 0,
    ) -> float:

        return self._calculate_index(
            probability=probability,
            odd=odd,
            expected_value=expected_value,
            market_count=market_count,
        )

    # ==========================================================
    # EXTRAÇÃO DE ODDS
    # ==========================================================

    def _extract_market_data(
        self,
        event: Dict[str, Any],
    ) -> Dict[
        str,
        Dict[
            str,
            Dict[str, Any]
        ]
    ]:
        """
        Organiza as odds recebidas da Pipeline.

        Estrutura:

            mercado
                seleção
                    bookmakers
                    best_odd
                    odds

        Não altera o evento original.
        """

        result: Dict[
            str,
            Dict[
                str,
                Dict[str, Any]
            ]
        ] = {}

        market_odds = event.get(
            "market_odds",
            [],
        )

        if not isinstance(
            market_odds,
            list,
        ):
            return result

        for item in market_odds:

            if not isinstance(
                item,
                dict,
            ):
                continue

            market = str(
                item.get(
                    "market",
                    "",
                )
            ).strip()

            outcome = str(
                item.get(
                    "outcome",
                    "",
                )
            ).strip()

            bookmaker = str(
                item.get(
                    "bookmaker",
                    "",
                )
            ).strip()

            odd = self._safe_float(
                item.get(
                    "odd"
                )
            )

            if (
                not market
                or not outcome
                or not bookmaker
                or odd <= 1.0
            ):
                continue

            result.setdefault(
                market,
                {}
            )

            result[
                market
            ].setdefault(
                outcome,
                {
                    "odds": [],
                    "bookmakers": [],
                },
            )

            result[
                market
            ][
                outcome
            ][
                "odds"
            ].append(
                odd
            )

            result[
                market
            ][
                outcome
            ][
                "bookmakers"
            ].append(
                {
                    "name": bookmaker,
                    "odd": odd,
                }
            )

        return result

    # ==========================================================
    # MELHOR ODD
    # ==========================================================

    @staticmethod
    def _best_bookmaker(
        bookmakers: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Retorna a casa que oferece a maior odd para
        determinada seleção.
        """

        valid = []

        for bookmaker in bookmakers:

            if not isinstance(
                bookmaker,
                dict,
            ):
                continue

            odd = float(
                bookmaker.get(
                    "odd",
                    0,
                )
                or 0
            )

            if odd > 1.0:

                valid.append(
                    bookmaker
                )

        if not valid:
            return None

        return max(
            valid,
            key=lambda x: float(
                x.get(
                    "odd",
                    0,
                )
                or 0
            ),
        )

    # ==========================================================
    # ANÁLISE DOS EVENTOS
    # ==========================================================

    def analyze(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Analisa todos os eventos.

        Para cada seleção:

        - calcula consenso de mercado;
        - remove overround;
        - identifica melhor odd;
        - calcula EV;
        - calcula Índice OddReal;
        - calcula confiança;
        - calcula risco;
        - identifica Value Bet.
        """

        if not isinstance(
            events,
            list,
        ):
            return []

        analyses: List[
            Dict[str, Any]
        ] = []

        for event in events:

            try:

                event_analyses = (
                    self._analyze_event(
                        event
                    )
                )

                analyses.extend(
                    event_analyses
                )

            except Exception as exc:

                error(
                    "Erro ao analisar "
                    f"evento: {exc}"
                )

        info(
            f"{len(events)} eventos analisados."
        )

        return analyses

    # ==========================================================
    # ANÁLISE INDIVIDUAL DO EVENTO
    # ==========================================================

    def _analyze_event(
        self,
        event: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Analisa um evento individual.
        """

        if not isinstance(
            event,
            dict,
        ):
            return []

        event_id = event.get(
            "id"
        )

        home_team = event.get(
            "home_team",
            "Casa",
        )

        away_team = event.get(
            "away_team",
            "Fora",
        )

        market_data = (
            self._extract_market_data(
                event
            )
        )

        results: List[
            Dict[str, Any]
        ] = []

        for market, outcomes in market_data.items():

            # --------------------------------------------------
            # CONSTRUÇÃO DO MERCADO
            # --------------------------------------------------

            market_outcomes = []

            for outcome_name, data in outcomes.items():

                odds = data.get(
                    "odds",
                    [],
                )

                if not odds:
                    continue

                # A odd usada pelo mercado é a média das casas.
                average_odd = (
                    sum(odds)
                    / len(odds)
                )

                market_outcomes.append(
                    {
                        "name": outcome_name,
                        "odd": average_odd,
                    }
                )

            if not market_outcomes:
                continue

            # --------------------------------------------------
            # PROBABILIDADES NORMALIZADAS
            # --------------------------------------------------

            probabilities = (
                self._market_probabilities(
                    market_outcomes
                )
            )

            if not probabilities:
                continue

            # --------------------------------------------------
            # CADA SELEÇÃO
            # --------------------------------------------------

            for outcome_name, data in outcomes.items():

                bookmakers = data.get(
                    "bookmakers",
                    [],
                )

                if not bookmakers:
                    continue

                best_bookmaker = (
                    self._best_bookmaker(
                        bookmakers
                    )
                )

                if best_bookmaker is None:
                    continue

                best_odd = self._safe_float(
                    best_bookmaker.get(
                        "odd"
                    )
                )

                if best_odd <= 1.0:
                    continue

                probability = (
                    probabilities.get(
                        outcome_name,
                        0.0,
                    )
                )

                if probability <= 0:
                    continue

                # ------------------------------------------------
                # EV CORRETO
                # ------------------------------------------------

                expected_value = (
                    self.expected_value(
                        probability,
                        best_odd,
                    )
                )

                # ------------------------------------------------
                # ÍNDICE
                # ------------------------------------------------

                oddreal_index = (
                    self._calculate_index(
                        probability=probability,
                        odd=best_odd,
                        expected_value=expected_value,
                        market_count=len(
                            bookmakers
                        ),
                    )
                )

                # ------------------------------------------------
                # CONFIANÇA
                # ------------------------------------------------

                confidence = (
                    self._confidence_level(
                        oddreal_index
                    )
                )

                # ------------------------------------------------
                # RISCO
                # ------------------------------------------------

                risk = (
                    self._risk_level(
                        odd=best_odd,
                        probability=probability,
                        index=oddreal_index,
                    )
                )

                # ------------------------------------------------
                # VALUE BET
                # ------------------------------------------------

                is_value = (
                    self._is_value_bet(
                        expected_value
                    )
                )

                # ------------------------------------------------
                # RESULTADO
                # ------------------------------------------------

                analysis = {

                    "event_id": event_id,

                    "home_team": (
                        home_team
                    ),

                    "away_team": (
                        away_team
                    ),

                    "market": market,

                    "outcome": (
                        outcome_name
                    ),

                    "selection": (
                        outcome_name
                    ),

                    "bookmaker": (
                        best_bookmaker.get(
                            "name",
                            "Desconhecida",
                        )
                    ),

                    "odd": round(
                        best_odd,
                        3,
                    ),

                    "best_odd": round(
                        best_odd,
                        3,
                    ),

                    "probability": round(
                        probability,
                        3,
                    ),

                    "market_probability": round(
                        probability,
                        3,
                    ),

                    "probability_source":
                        "market_consensus",

                    "expected_value":
                        round(
                            expected_value,
                            3,
                        ),

                    "average_odd":
                        round(
                            (
                                sum(
                                    data.get(
                                        "odds",
                                        [],
                                    )
                                )
                                / len(
                                    data.get(
                                        "odds",
                                        [],
                                    )
                                )
                            ),
                            3,
                        ),

                    "market_variation":
                        round(
                            self._variation(
                                data.get(
                                    "odds",
                                    [],
                                )
                            ),
                            3,
                        ),

                    "oddreal_index":
                        oddreal_index,

                    "confidence_level":
                        confidence,

                    "confidence":
                        confidence,

                    "risk":
                        risk,

                    "is_value_bet":
                        is_value,

                    "market_count":
                        len(
                            bookmakers
                        ),

                    "available_bookmakers":
                        [
                            b.get(
                                "name"
                            )
                            for b in bookmakers
                            if isinstance(
                                b,
                                dict,
                            )
                        ],
                }

                results.append(
                    analysis
                )

        return results

    # ==========================================================
    # VARIAÇÃO DAS ODDS
    # ==========================================================

    @staticmethod
    def _variation(
        odds: List[float],
    ) -> float:
        """
        Calcula a variação percentual entre a menor e maior odd.
        """

        valid = []

        for odd in odds:

            try:

                value = float(
                    odd
                )

                if value > 1.0:
                    valid.append(
                        value
                    )

            except (
                TypeError,
                ValueError,
            ):
                continue

        if len(valid) < 2:
            return 0.0

        minimum = min(
            valid
        )

        maximum = max(
            valid
        )

        if minimum <= 0:
            return 0.0

        return round(
            (
                (
                    maximum
                    - minimum
                )
                / minimum
            )
            * 100.0,
            4,
        )

    # ==========================================================
    # VALUE BETS
    # ==========================================================

    def value_bets(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Retorna somente Value Bets reais segundo o critério
        quantitativo definido.

        Critério:

            EV >= 5%

        Portanto:

            EV = -2.56%  -> NÃO
            EV = -1.20%  -> NÃO
            EV =  1.21%  -> NÃO
            EV =  4.99%  -> NÃO
            EV =  5.00%  -> SIM
            EV = 10.00%  -> SIM
        """

        if not isinstance(
            analyses,
            list,
        ):
            return []

        values = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            ev = self._safe_float(
                analysis.get(
                    "expected_value"
                )
            )

            # Nunca confiar apenas no campo
            # is_value_bet vindo de outro módulo.
            # Recalculamos a decisão.
            is_value = (
                ev
                >= self.VALUE_BET_MIN_EV
            )

            analysis[
                "is_value_bet"
            ] = is_value

            if is_value:

                values.append(
                    analysis
                )

        values.sort(
            key=lambda x: self._safe_float(
                x.get(
                    "expected_value"
                )
            ),
            reverse=True,
        )

        info(
            f"{len(values)} Value Bets encontradas."
        )

        return values

    # ==========================================================
    # MELHOR OPORTUNIDADE
    # ==========================================================

    def best_opportunity(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Retorna a melhor oportunidade geral.

        Prioridade:

        1. maior Índice OddReal;
        2. maior EV;
        3. maior probabilidade.
        """

        if not analyses:
            return None

        valid = [
            item
            for item in analyses
            if isinstance(
                item,
                dict,
            )
        ]

        if not valid:
            return None

        return max(
            valid,
            key=lambda x: (
                self._safe_float(
                    x.get(
                        "oddreal_index"
                    )
                ),
                self._safe_float(
                    x.get(
                        "expected_value"
                    )
                ),
                self._safe_float(
                    x.get(
                        "probability"
                    )
                ),
            ),
        )

    # ==========================================================
    # MELHOR VALUE BET
    # ==========================================================

    def best_value_bet(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """
        Retorna a melhor Value Bet.

        Somente EV >= 5% participa.
        """

        values = self.value_bets(
            analyses
        )

        if not values:
            return None

        return max(
            values,
            key=lambda x: (
                self._safe_float(
                    x.get(
                        "expected_value"
                    )
                ),
                self._safe_float(
                    x.get(
                        "oddreal_index"
                    )
                ),
            ),
        )

    # ==========================================================
    # RESUMO
    # ==========================================================

    def summary(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Gera resumo estatístico das análises.
        """

        if not isinstance(
            analyses,
            list,
        ):
            analyses = []

        total = len(
            analyses
        )

        value_bets = self.value_bets(
            analyses
        )

        if total == 0:

            return {
                "total_analyses": 0,
                "total_value_bets": 0,
                "average_index": 0.0,
                "average_ev": 0.0,
                "best_opportunity": None,
            }

        indices = [
            self._safe_float(
                item.get(
                    "oddreal_index"
                )
            )
            for item in analyses
            if isinstance(
                item,
                dict,
            )
        ]

        evs = [
            float(
                item.get(
                    "expected_value",
                    0.0,
                )
                or 0.0
            )
            for item in analyses
            if isinstance(
                item,
                dict,
            )
        ]

        average_index = (
            sum(indices)
            / len(indices)
            if indices
            else 0.0
        )

        average_ev = (
            sum(evs)
            / len(evs)
            if evs
            else 0.0
        )

        return {

            "total_analyses":
                total,

            "total_value_bets":
                len(
                    value_bets
                ),

            "average_index":
                round(
                    average_index,
                    2,
                ),

            "average_ev":
                round(
                    average_ev,
                    3,
                ),

            "best_opportunity":
                self.best_opportunity(
                    analyses
                ),

            "best_value_bet":
                self.best_value_bet(
                    analyses
                ),
        }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()
              
