
"""
OddReal 2.0
modules/statistics.py

Motor estatístico.

Responsável por:

- Estatísticas das equipes
- Forma recente
- Média de gols
- Mandante x Visitante
- BTTS
- Over/Under
- Clean Sheets
- Tendências
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

import statistics
import pandas as pd


# ==========================================================
# MODELOS
# ==========================================================

@dataclass
class TeamStatistics:

    team: str

    matches: int

    wins: int

    draws: int

    losses: int

    goals_for: int

    goals_against: int

    points: int

    form: float


# ==========================================================
# ENGINE
# ==========================================================

class StatisticsEngine:

    def __init__(self):

        self.minimum_matches = 5

        self.form_weight = 0.40

        self.attack_weight = 0.30

        self.defense_weight = 0.30


# ==========================================================
# APROVEITAMENTO
# ==========================================================

    def win_rate(
        self,
        wins: int,
        matches: int
    ) -> float:

        if matches == 0:

            return 0

        return round(

            wins / matches * 100,

            2

        )


# ==========================================================
# MÉDIA DE GOLS
# ==========================================================

    def average_goals(
        self,
        goals: int,
        matches: int
    ) -> float:

        if matches == 0:

            return 0

        return round(

            goals / matches,

            2

        )


# ==========================================================
# MÉDIA SOFRIDA
# ==========================================================

    def average_conceded(
        self,
        goals: int,
        matches: int
    ) -> float:

        if matches == 0:

            return 0

        return round(

            goals / matches,

            2

        )


# ==========================================================
# SALDO DE GOLS
# ==========================================================

    def goal_difference(
        self,
        goals_for: int,
        goals_against: int
    ) -> int:

        return goals_for - goals_against


# ==========================================================
# PONTOS POR JOGO
# ==========================================================

    def points_per_game(
        self,
        points: int,
        matches: int
    ) -> float:

        if matches == 0:

            return 0

        return round(

            points / matches,

            2

        )


# ==========================================================
# FORMA RECENTE
# ==========================================================

    def recent_form(
        self,
        results: List[str]
    ) -> float:

        """
        W = Vitória
        D = Empate
        L = Derrota
        """

        score = 0

        for result in results:

            if result == "W":

                score += 3

            elif result == "D":

                score += 1

        maximum = len(results) * 3

        if maximum == 0:

            return 0

        return round(

            score / maximum * 100,

            2

        )
