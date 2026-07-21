"""
OddReal 2.0

Motor matemático das odds.

Responsável por:

- Conversões de odds
- Fair Odds
- Value
- Arbitragem
- CLV
- Kelly Criterion
- Stake
- ROI
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import math


# ==========================================================
# MODELO
# ==========================================================

@dataclass
class OddsResult:

    bookmaker: str

    odd: float

    probability: float

    fair_odd: float

    edge: float

    expected_value: float


# ==========================================================
# ENGINE
# ==========================================================

class OddsEngine:

    def __init__(self):

        self.minimum_odd = 1.01

        self.maximum_probability = 0.999

        self.minimum_probability = 0.001

        self.kelly_fraction = 1.0


# ==========================================================
# DECIMAL -> PROBABILIDADE
# ==========================================================

    def implied_probability(
        self,
        odd: float
    ) -> float:

        if odd <= 1:

            return 0

        return 1 / odd


# ==========================================================
# PROBABILIDADE -> ODD
# ==========================================================

    def probability_to_odd(
        self,
        probability: float
    ) -> float:

        if probability <= 0:

            return 0

        return 1 / probability


# ==========================================================
# AMERICANA -> DECIMAL
# ==========================================================

    def american_to_decimal(
        self,
        american: float
    ) -> float:

        if american > 0:

            return (american / 100) + 1

        return (100 / abs(american)) + 1


# ==========================================================
# DECIMAL -> AMERICANA
# ==========================================================

    def decimal_to_american(
        self,
        decimal: float
    ) -> float:

        if decimal >= 2:

            return (decimal - 1) * 100

        return -100 / (decimal - 1)


# ==========================================================
# DECIMAL -> FRACIONÁRIA
# ==========================================================

    def decimal_to_fractional(
        self,
        decimal: float
    ):

        decimal -= 1

        numerator = round(decimal * 100)

        denominator = 100

        divisor = math.gcd(
            numerator,
            denominator
        )

        return (

            numerator // divisor,

            denominator // divisor

        )


# ==========================================================
# FAIR ODD
# ==========================================================

    def fair_odd(
        self,
        probability: float
    ) -> float:

        if probability <= 0:

            return 0

        return 1 / probability
      # ==========================================================
# EXPECTED VALUE (EV)
# ==========================================================

    def expected_value(
        self,
        odd: float,
        probability: float
    ) -> float:
        """
        Calcula o Valor Esperado (EV) em porcentagem.
        """
        return ((odd * probability) - 1) * 100


# ==========================================================
# EDGE
# ==========================================================

    def edge(
        self,
        offered_odd: float,
        fair_odd: float
    ) -> float:

        if fair_odd <= 0:
            return 0

        return ((offered_odd / fair_odd) - 1) * 100


# ==========================================================
# RETORNO LÍQUIDO
# ==========================================================

    def net_profit(
        self,
        stake: float,
        odd: float
    ) -> float:

        return (stake * odd) - stake


# ==========================================================
# RETORNO TOTAL
# ==========================================================

    def total_return(
        self,
        stake: float,
        odd: float
    ) -> float:

        return stake * odd


# ==========================================================
# ROI
# ==========================================================

    def roi(
        self,
        profit: float,
        invested: float
    ) -> float:

        if invested <= 0:
            return 0

        return (profit / invested) * 100


# ==========================================================
# KELLY CRITERION
# ==========================================================

    def kelly(
        self,
        odd: float,
        probability: float
    ) -> float:
        """
        Percentual ideal da banca para apostar.
        """

        b = odd - 1

        p = probability

        q = 1 - p

        if b <= 0:
            return 0

        value = ((b * p) - q) / b

        return max(0.0, value)


# ==========================================================
# STAKE RECOMENDADA
# ==========================================================

    def recommended_stake(
        self,
        bankroll: float,
        odd: float,
        probability: float
    ) -> float:

        percentage = self.kelly(
            odd,
            probability
        )

        return round(
            bankroll * percentage * self.kelly_fraction,
            2
        )


# ==========================================================
# CLASSIFICAÇÃO DA ODD
# ==========================================================

    def classify_odd(
        self,
        ev: float,
        edge: float
    ) -> str:

        if ev >= 15 and edge >= 10:
            return "EXCELENTE"

        if ev >= 8 and edge >= 5:
            return "MUITO BOA"

        if ev >= 3:
            return "BOA"

        if ev >= 0:
            return "NEUTRA"

        return "RUIM"
      # ==========================================================
# ARBITRAGEM (SUREBET)
# ==========================================================

    def arbitrage_percentage(
        self,
        odds: List[float]
    ) -> float:
        """
        Retorna o percentual da arbitragem.
        Valores abaixo de 100 indicam Surebet.
        """

        if not odds:
            return 0

        total = 0.0

        for odd in odds:

            if odd > 1:

                total += 1 / odd

        return total * 100


# ==========================================================
# EXISTE ARBITRAGEM?
# ==========================================================

    def is_arbitrage(
        self,
        odds: List[float]
    ) -> bool:

        return self.arbitrage_percentage(
            odds
        ) < 100


# ==========================================================
# LUCRO DA ARBITRAGEM
# ==========================================================

    def arbitrage_profit(
        self,
        odds: List[float],
        investment: float
    ) -> float:

        percentage = self.arbitrage_percentage(
            odds
        )

        if percentage >= 100:

            return 0

        return round(

            investment *

            (
                (100 / percentage) - 1

            ),

            2

        )


# ==========================================================
# DISTRIBUIÇÃO DA BANCA
# ==========================================================

    def arbitrage_distribution(
        self,
        odds: List[float],
        investment: float
    ) -> List[float]:

        total = sum(

            1 / odd

            for odd in odds

        )

        stakes = []

        for odd in odds:

            value = (

                investment

                *

                ((1 / odd) / total)

            )

            stakes.append(

                round(value, 2)

            )

        return stakes


# ==========================================================
# MELHOR ODD
# ==========================================================

    def best_odd(
        self,
        bookmakers: Dict[str, float]
    ):

        if not bookmakers:

            return None

        bookmaker = max(

            bookmakers,

            key=bookmakers.get

        )

        return {

            "bookmaker": bookmaker,

            "odd": bookmakers[bookmaker]

        }


# ==========================================================
# PIOR ODD
# ==========================================================

    def worst_odd(
        self,
        bookmakers: Dict[str, float]
    ):

        if not bookmakers:

            return None

        bookmaker = min(

            bookmakers,

            key=bookmakers.get

        )

        return {

            "bookmaker": bookmaker,

            "odd": bookmakers[bookmaker]

        }


# ==========================================================
# DIFERENÇA ENTRE ODDS
# ==========================================================

    def market_variation(
        self,
        bookmakers: Dict[str, float]
    ) -> float:

        if not bookmakers:

            return 0

        values = list(

            bookmakers.values()

        )

        return round(

            max(values) - min(values),

            3

        )
      # ==========================================================
# HISTÓRICO DAS ODDS
# ==========================================================

    def price_movement(
        self,
        opening_odd: float,
        current_odd: float
    ) -> dict:
        """
        Analisa a movimentação da odd entre a abertura e o momento atual.
        """

        if opening_odd <= 0:
            return {}

        variation = (
            (current_odd - opening_odd)
            / opening_odd
        ) * 100

        if variation < -5:
            trend = "FORTE_QUEDA"

        elif variation < -1:
            trend = "QUEDA"

        elif variation > 5:
            trend = "FORTE_ALTA"

        elif variation > 1:
            trend = "ALTA"

        else:
            trend = "ESTÁVEL"

        return {

            "opening_odd": opening_odd,

            "current_odd": current_odd,

            "variation": round(
                variation,
                2
            ),

            "trend": trend

        }


# ==========================================================
# CLOSING LINE VALUE (CLV)
# ==========================================================

    def closing_line_value(
        self,
        bet_odd: float,
        closing_odd: float
    ) -> float:

        if bet_odd <= 0 or closing_odd <= 0:

            return 0

        clv = (

            (bet_odd - closing_odd)

            /

            closing_odd

        ) * 100

        return round(

            clv,

            2

        )


# ==========================================================
# STEAM MOVE
# ==========================================================

    def detect_steam_move(
        self,
        opening_odd: float,
        current_odd: float,
        threshold: float = 5
    ) -> bool:

        if opening_odd <= 0:

            return False

        change = abs(

            (

                current_odd

                -

                opening_odd

            )

            /

            opening_odd

        ) * 100

        return change >= threshold


# ==========================================================
# MÉDIA DAS ODDS
# ==========================================================

    def average_odd(
        self,
        odds: List[float]
    ) -> float:

        if not odds:

            return 0

        return round(

            sum(odds)

            /

            len(odds),

            3

        )


# ==========================================================
# DESVIO ENTRE AS CASAS
# ==========================================================

    def odds_deviation(
        self,
        odds: List[float]
    ) -> float:

        if len(odds) <= 1:

            return 0

        average = self.average_odd(

            odds

        )

        variance = sum(

            (

                odd

                -

                average

            ) ** 2

            for odd in odds

        ) / len(odds)

        return round(

            math.sqrt(

                variance

            ),

            4

        )


# ==========================================================
# MERCADO VOLÁTIL
# ==========================================================

    def volatile_market(
        self,
        odds: List[float],
        limit: float = 0.12
    ) -> bool:

        deviation = self.odds_deviation(

            odds

        )

        return deviation >= limit
      # ==========================================================
# SCANNER DE MERCADO
# ==========================================================

    def scan_market(
        self,
        market: str,
        bookmakers: Dict[str, float]
    ) -> Dict:

        if not bookmakers:

            return {}

        best = self.best_odd(bookmakers)
        worst = self.worst_odd(bookmakers)

        odds = list(bookmakers.values())

        return {

            "market": market,

            "bookmakers": len(bookmakers),

            "best_bookmaker": best["bookmaker"],

            "best_odd": best["odd"],

            "worst_bookmaker": worst["bookmaker"],

            "worst_odd": worst["odd"],

            "average_odd": self.average_odd(odds),

            "variation": self.market_variation(bookmakers),

            "volatility": self.volatile_market(odds),

            "arbitrage": self.is_arbitrage(odds)

        }


# ==========================================================
# SCORE DO MERCADO
# ==========================================================

    def market_score(
        self,
        bookmakers: Dict[str, float]
    ) -> float:

        if not bookmakers:

            return 0

        odds = list(bookmakers.values())

        score = 100

        score -= self.odds_deviation(odds) * 100

        if self.is_arbitrage(odds):

            score += 15

        score = max(0, min(score, 100))

        return round(score, 2)


# ==========================================================
# RANKING DAS CASAS
# ==========================================================

    def bookmaker_ranking(
        self,
        bookmakers: Dict[str, float]
    ) -> List[Dict]:

        ranking = []

        average = self.average_odd(
            list(bookmakers.values())
        )

        for bookmaker, odd in bookmakers.items():

            ranking.append({

                "bookmaker": bookmaker,

                "odd": odd,

                "difference": round(

                    odd - average,

                    3

                )

            })

        ranking.sort(

            key=lambda x: x["odd"],

            reverse=True

        )

        return ranking


# ==========================================================
# ALERTAS
# ==========================================================

    def generate_alerts(
        self,
        bookmakers: Dict[str, float]
    ) -> List[str]:

        alerts = []

        odds = list(bookmakers.values())

        if self.is_arbitrage(odds):

            alerts.append(

                "🚨 Oportunidade de arbitragem encontrada."

            )

        if self.volatile_market(odds):

            alerts.append(

                "📊 Mercado com alta volatilidade."

            )

        variation = self.market_variation(bookmakers)

        if variation >= 0.30:

            alerts.append(

                f"📈 Diferença elevada entre odds ({variation:.2f})."

            )

        return alerts


# ==========================================================
# RELATÓRIO COMPLETO
# ==========================================================

    def market_report(
        self,
        market: str,
        bookmakers: Dict[str, float]
    ) -> Dict:

        return {

            "scan": self.scan_market(

                market,

                bookmakers

            ),

            "score": self.market_score(

                bookmakers

            ),

            "ranking": self.bookmaker_ranking(

                bookmakers

            ),

            "alerts": self.generate_alerts(

                bookmakers

            )

        }
      # ==========================================================
# PROCESSAMENTO DE TODOS OS MERCADOS
# ==========================================================

    def process_markets(
        self,
        markets: Dict[str, Dict[str, float]]
    ) -> Dict:

        reports = {}

        for market, bookmakers in markets.items():

            reports[market] = self.market_report(
                market,
                bookmakers
            )

        return reports


# ==========================================================
# MELHOR MERCADO
# ==========================================================

    def best_market(
        self,
        reports: Dict
    ):

        if not reports:
            return None

        best = None
        best_score = -1

        for market, report in reports.items():

            score = report["score"]

            if score > best_score:

                best_score = score

                best = {
                    "market": market,
                    "score": score,
                    "report": report
                }

        return best


# ==========================================================
# RESUMO GERAL
# ==========================================================

    def summary(
        self,
        reports: Dict
    ) -> Dict:

        if not reports:

            return {

                "markets": 0,

                "alerts": 0,

                "average_score": 0

            }

        scores = []

        alerts = 0

        for report in reports.values():

            scores.append(report["score"])

            alerts += len(report["alerts"])

        return {

            "markets": len(reports),

            "alerts": alerts,

            "average_score": round(

                sum(scores) / len(scores),

                2

            )

        }


# ==========================================================
# EXPORTAÇÃO PARA PANDAS
# ==========================================================

    def to_dataframe(
        self,
        reports: Dict
    ):

        import pandas as pd

        rows = []

        for market, report in reports.items():

            scan = report["scan"]

            rows.append({

                "Market": market,

                "Score": report["score"],

                "Best Bookmaker":
                    scan["best_bookmaker"],

                "Best Odd":
                    scan["best_odd"],

                "Average Odd":
                    scan["average_odd"],

                "Variation":
                    scan["variation"],

                "Volatility":
                    scan["volatility"],

                "Arbitrage":
                    scan["arbitrage"]

            })

        return pd.DataFrame(rows)


# ==========================================================
# RESET
# ==========================================================

    def reset(self):

        self.kelly_fraction = 1.0

        return True


# ==========================================================
# STATUS
# ==========================================================

    def status(self):

        return {

            "module": "Odds Engine",

            "version": "2.0",

            "ready": True,

            "features": [

                "Fair Odds",

                "Expected Value",

                "Kelly",

                "ROI",

                "Arbitrage",

                "CLV",

                "Steam Move",

                "Scanner",

                "Ranking",

                "Alerts",

                "Market Score"

            ]

        }
