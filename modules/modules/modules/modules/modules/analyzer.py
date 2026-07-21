"""
OddReal 2.0
modules/analyzer.py

Motor de análise das odds.

Responsável por:

- Probabilidade implícita
- Overround
- Fair Odds
- Expected Value (EV)
- Edge
- Ranking de oportunidades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import math
import pandas as pd


# ============================================================
# MODELOS
# ============================================================

@dataclass
class BetAnalysis:

    market: str

    bookmaker: str

    odd: float

    implied_probability: float

    fair_probability: float

    fair_odd: float

    expected_value: float

    edge: float

    confidence: float

    is_value_bet: bool


# ============================================================
# ANALYZER
# ============================================================

class Analyzer:

    """
    Motor estatístico principal.

    Todas as análises passam por aqui.
    """

    def __init__(self):

        self.value_threshold = 3.0

        self.min_confidence = 60

        self.max_probability = 0.999

        self.min_probability = 0.001


# ============================================================
# PROBABILIDADE IMPLÍCITA
# ============================================================

    def implied_probability(
        self,
        odd: float
    ) -> float:

        """
        Converte odd em probabilidade.
        """

        if odd <= 1:
            return 0

        return 1 / odd


# ============================================================
# OVERROUND
# ============================================================

    def overround(
        self,
        odds: List[float]
    ) -> float:

        """
        Calcula margem da casa.
        """

        total = 0

        for odd in odds:

            if odd > 1:

                total += 1 / odd

        return (total - 1) * 100


# ============================================================
# NORMALIZAÇÃO DAS PROBABILIDADES
# ============================================================

    def normalize_probabilities(
        self,
        odds: List[float]
    ) -> List[float]:

        probs = []

        for odd in odds:

            probs.append(
                self.implied_probability(
                    odd
                )
            )

        total = sum(probs)

        if total == 0:

            return probs

        return [

            p / total

            for p in probs

        ]


# ============================================================
# FAIR ODDS
# ============================================================

    def fair_odds(
        self,
        odds: List[float]
    ) -> List[float]:

        probabilities = self.normalize_probabilities(
            odds
        )

        fair = []

        for p in probabilities:

            if p == 0:

                fair.append(0)

            else:

                fair.append(
                    1 / p
                )

        return fair


# ============================================================
# EXPECTED VALUE
# ============================================================

    def expected_value(
        self,
        odd: float,
        probability: float
    ) -> float:

        """
        EV em percentual.
        """

        return (
            (odd * probability) - 1
        ) * 100


# ============================================================
# EDGE
# ============================================================

    def edge(
        self,
        offered_odd: float,
        fair_odd: float
    ) -> float:

        if fair_odd <= 0:

            return 0

        return (
            (
                offered_odd
                /
                fair_odd
            )
            -
            1
        ) * 100
      # ============================================================
# SCORE DE CONFIANÇA
# ============================================================

    def confidence_score(
        self,
        expected_value: float,
        edge: float,
        probability: float
    ) -> float:
        """
        Calcula um score de confiança entre 0 e 100.
        """

        score = 50.0

        score += min(expected_value, 20) * 1.5
        score += min(edge, 15) * 1.2
        score += probability * 20

        score = max(0.0, min(score, 100.0))

        return round(score, 2)


# ============================================================
# VALUE BET
# ============================================================

    def is_value_bet(
        self,
        expected_value: float,
        edge: float
    ) -> bool:

        return (
            expected_value >= self.value_threshold
            and
            edge > 0
        )


# ============================================================
# ANALISAR UMA ODD
# ============================================================

    def analyze_odd(
        self,
        market: str,
        bookmaker: str,
        offered_odd: float,
        fair_probability: float
    ) -> BetAnalysis:

        implied = self.implied_probability(
            offered_odd
        )

        if fair_probability <= 0:

            fair_probability = implied

        fair_odd = 1 / fair_probability

        ev = self.expected_value(
            offered_odd,
            fair_probability
        )

        edge = self.edge(
            offered_odd,
            fair_odd
        )

        confidence = self.confidence_score(
            ev,
            edge,
            fair_probability
        )

        value = self.is_value_bet(
            ev,
            edge
        )

        return BetAnalysis(

            market=market,

            bookmaker=bookmaker,

            odd=offered_odd,

            implied_probability=round(
                implied * 100,
                2
            ),

            fair_probability=round(
                fair_probability * 100,
                2
            ),

            fair_odd=round(
                fair_odd,
                3
            ),

            expected_value=round(
                ev,
                2
            ),

            edge=round(
                edge,
                2
            ),

            confidence=round(
                confidence,
                2
            ),

            is_value_bet=value
        )


# ============================================================
# COMPARAR BOOKMAKERS
# ============================================================

    def compare_bookmakers(
        self,
        market: str,
        odds: Dict[str, float]
    ) -> List[BetAnalysis]:

        fair = self.fair_odds(
            list(odds.values())
        )

        analyses = []

        for bookmaker, odd in odds.items():

            probability = (
                1 / fair.pop(0)
            )

            analyses.append(

                self.analyze_odd(

                    market=market,

                    bookmaker=bookmaker,

                    offered_odd=odd,

                    fair_probability=probability
                )

            )

        return analyses
      # ============================================================
# RANKING DAS MELHORES OPORTUNIDADES
# ============================================================

    def rank_opportunities(
        self,
        analyses: List[BetAnalysis]
    ) -> List[BetAnalysis]:

        """
        Ordena as apostas da melhor para a pior.
        """

        return sorted(

            analyses,

            key=lambda item: (

                item.expected_value,

                item.edge,

                item.confidence

            ),

            reverse=True

        )
# ============================================================
# RANKING DAS MELHORES OPORTUNIDADES
# ============================================================

    def rank_opportunities(
        self,
        analyses: List[BetAnalysis]
    ) -> List[BetAnalysis]:

        """
        Ordena as apostas da melhor para a pior.
        """

        return sorted(

            analyses,

            key=lambda item: (

                item.expected_value,

                item.edge,

                item.confidence

            ),

            reverse=True

        )


# ============================================================
# FILTRAR VALUE BETS
# ============================================================

    def filter_value_bets(
        self,
        analyses: List[BetAnalysis]
    ) -> List[BetAnalysis]:

        return [

            analysis

            for analysis in analyses

            if analysis.is_value_bet

        ]


# ============================================================
# FILTRAR POR CONFIANÇA
# ============================================================

    def filter_by_confidence(
        self,
        analyses: List[BetAnalysis],
        minimum: float = None
    ) -> List[BetAnalysis]:

        if minimum is None:

            minimum = self.min_confidence

        return [

            analysis

            for analysis in analyses

            if analysis.confidence >= minimum

        ]


# ============================================================
# CONVERTER PARA DATAFRAME
# ============================================================

    def to_dataframe(
        self,
        analyses: List[BetAnalysis]
    ) -> pd.DataFrame:

        rows = []

        for analysis in analyses:

            rows.append({

                "Market":
                    analysis.market,

                "Bookmaker":
                    analysis.bookmaker,

                "Odd":
                    analysis.odd,

                "Implied Probability":
                    analysis.implied_probability,

                "Fair Probability":
                    analysis.fair_probability,

                "Fair Odd":
                    analysis.fair_odd,

                "Expected Value":
                    analysis.expected_value,

                "Edge":
                    analysis.edge,

                "Confidence":
                    analysis.confidence,

                "Value Bet":
                    analysis.is_value_bet

            })

        return pd.DataFrame(rows)


# ============================================================
# ANÁLISE COMPLETA DE UM MERCADO
# ============================================================

    def analyze_market(
        self,
        market: str,
        odds: Dict[str, float]
    ) -> pd.DataFrame:

        analyses = self.compare_bookmakers(

            market,

            odds

        )

        analyses = self.filter_by_confidence(

            analyses

        )

        analyses = self.rank_opportunities(

            analyses

        )

        return self.to_dataframe(

            analyses

        )
      # ============================================================
# ESTATÍSTICAS DO MERCADO
# ============================================================

    def market_statistics(
        self,
        analyses: List[BetAnalysis]
    ) -> Dict:

        if not analyses:

            return {}

        odds = [a.odd for a in analyses]

        evs = [a.expected_value for a in analyses]

        edges = [a.edge for a in analyses]

        confidence = [a.confidence for a in analyses]

        value_bets = len(

            [

                a

                for a in analyses

                if a.is_value_bet

            ]

        )

        return {

            "bookmakers": len(analyses),

            "average_odd": round(sum(odds) / len(odds), 3),

            "highest_odd": round(max(odds), 3),

            "lowest_odd": round(min(odds), 3),

            "average_ev": round(sum(evs) / len(evs), 2),

            "average_edge": round(sum(edges) / len(edges), 2),

            "average_confidence": round(

                sum(confidence) / len(confidence),

                2

            ),

            "value_bets": value_bets

        }


# ============================================================
# SCORE GERAL DO MERCADO
# ============================================================

    def market_score(
        self,
        analyses: List[BetAnalysis]
    ) -> float:

        if not analyses:

            return 0

        stats = self.market_statistics(

            analyses

        )

        score = (

            stats["average_confidence"] * 0.50 +

            stats["average_edge"] * 0.30 +

            stats["average_ev"] * 0.20

        )

        return round(

            max(0, min(score, 100)),

            2

        )


# ============================================================
# DETECÇÃO DE DISTORÇÕES
# ============================================================

    def detect_market_distortion(
        self,
        odds: Dict[str, float]
    ) -> Dict:

        if len(odds) < 2:

            return {

                "distortion": False,

                "difference": 0

            }

        values = list(

            odds.values()

        )

        maximum = max(values)

        minimum = min(values)

        difference = (

            (

                maximum

                -

                minimum

            )

            /

            minimum

        ) * 100

        return {

            "distortion":

                difference >= 5,

            "difference":

                round(

                    difference,

                    2

                )

        }


# ============================================================
# EXPORTAÇÃO PARA IA
# ============================================================

    def export_for_ai(
        self,
        analyses: List[BetAnalysis]
    ) -> pd.DataFrame:

        rows = []

        for a in analyses:

            rows.append({

                "odd": a.odd,

                "fair_odd": a.fair_odd,

                "ev": a.expected_value,

                "edge": a.edge,

                "confidence": a.confidence,

                "value_bet": int(

                    a.is_value_bet

                )

            })

        return pd.DataFrame(rows)
# ============================================================
# ANÁLISE DE TODOS OS MERCADOS
# ============================================================

    def analyze_all_markets(
        self,
        markets: Dict[str, Dict[str, float]]
    ) -> Dict[str, pd.DataFrame]:

        """
        Analisa todos os mercados disponíveis
        de uma partida.

        Exemplo:

        {
            "Match Winner": {...},
            "Over 2.5": {...},
            "BTTS": {...}
        }
        """

        results = {}

        for market_name, bookmakers in markets.items():

            try:

                results[market_name] = self.analyze_market(

                    market_name,

                    bookmakers

                )

            except Exception:

                continue

        return results


# ============================================================
# RANKING GLOBAL
# ============================================================

    def global_ranking(
        self,
        analyses: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:

        dfs = []

        for market, dataframe in analyses.items():

            if dataframe.empty:

                continue

            temp = dataframe.copy()

            temp["Market"] = market

            dfs.append(temp)

        if not dfs:

            return pd.DataFrame()

        ranking = pd.concat(

            dfs,

            ignore_index=True

        )

        ranking = ranking.sort_values(

            by=[

                "Confidence",

                "Expected Value",

                "Edge"

            ],

            ascending=False

        )

        ranking.reset_index(

            drop=True,

            inplace=True

        )

        return ranking


# ============================================================
# ALERTAS
# ============================================================

    def generate_alerts(
        self,
        ranking: pd.DataFrame
    ) -> List[str]:

        alerts = []

        if ranking.empty:

            return alerts

        for _, row in ranking.iterrows():

            if row["Confidence"] >= 85:

                alerts.append(

                    f"🔥 Alta confiança em "
                    f"{row['Market']} "
                    f"({row['Bookmaker']})"

                )

            if row["Expected Value"] >= 10:

                alerts.append(

                    f"💰 EV elevado "
                    f"({row['Expected Value']}%)"

                )

            if row["Edge"] >= 8:

                alerts.append(

                    f"📈 Edge positivo "
                    f"({row['Edge']}%)"

                )

        return alerts


# ============================================================
# RESUMO DA PARTIDA
# ============================================================

    def match_summary(
        self,
        analyses: Dict[str, pd.DataFrame]
    ) -> Dict:

        ranking = self.global_ranking(

            analyses

        )

        alerts = self.generate_alerts(

            ranking

        )

        return {

            "markets":

                len(analyses),

            "opportunities":

                len(ranking),

            "alerts":

                alerts,

            "best_opportunity":

                None if ranking.empty

                else ranking.iloc[0].to_dict()

        }
      # ============================================================
# CACHE INTERNO
# ============================================================

    def clear_cache(self):

        """
        Limpa estruturas temporárias.
        """

        self._cache = {}

        return True


# ============================================================
# VALIDAÇÃO DAS ODDS
# ============================================================

    def validate_odds(
        self,
        odds: Dict[str, float]
    ) -> bool:

        if not odds:

            return False

        for odd in odds.values():

            if odd is None:
                return False

            if not isinstance(odd, (int, float)):
                return False

            if odd <= 1:
                return False

        return True


# ============================================================
# PROCESSAMENTO COMPLETO
# ============================================================

    def process(
        self,
        markets: Dict[str, Dict[str, float]]
    ) -> Dict:

        output = {

            "markets": {},

            "ranking": None,

            "summary": None,

            "alerts": []

        }

        analyses = {}

        for market, odds in markets.items():

            if not self.validate_odds(odds):

                continue

            try:

                analyses[market] = self.analyze_market(

                    market,

                    odds

                )

            except Exception:

                continue

        ranking = self.global_ranking(

            analyses

        )

        summary = self.match_summary(

            analyses

        )

        alerts = self.generate_alerts(

            ranking

        )

        output["markets"] = analyses

        output["ranking"] = ranking

        output["summary"] = summary

        output["alerts"] = alerts

        return output


# ============================================================
# MELHOR OPORTUNIDADE
# ============================================================

    def best_bet(
        self,
        ranking: pd.DataFrame
    ):

        if ranking.empty:

            return None

        return ranking.iloc[0].to_dict()


# ============================================================
# TOP N OPORTUNIDADES
# ============================================================

    def top_opportunities(
        self,
        ranking: pd.DataFrame,
        limit: int = 10
    ):

        if ranking.empty:

            return pd.DataFrame()

        return ranking.head(limit)


# ============================================================
# EXPORTAÇÃO CSV
# ============================================================

    def export_csv(
        self,
        dataframe: pd.DataFrame,
        filename: str
    ):

        dataframe.to_csv(

            filename,

            index=False,

            encoding="utf-8"

        )

        return filename


# ============================================================
# EXPORTAÇÃO EXCEL
# ============================================================

    def export_excel(
        self,
        dataframe: pd.DataFrame,
        filename: str
    ):

        dataframe.to_excel(

            filename,

            index=False

        )

        return filename


# ============================================================
# STATUS
# ============================================================

    def status(self):

        return {

            "module": "Analyzer",

            "version": "2.0",

            "ready": True,

            "features": [

                "Probability",

                "Overround",

                "Fair Odds",

                "Expected Value",

                "Edge",

                "Value Bets",

                "Confidence",

                "Ranking",

                "Alerts",

                "Statistics",

                "AI Export"

            ]

        }
