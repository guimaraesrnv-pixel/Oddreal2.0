from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    """
    Modelo de um evento esportivo.
    """

    id: str

    sport: str

    league: str

    home_team: str

    away_team: str

    commence_time: datetime

    bookmaker: Optional[str] = None

    market: Optional[str] = None

    status: str = "scheduled"

    def to_dict(self) -> dict:
        """
        Converte o objeto para dicionário.
        """

        return {

            "id": self.id,

            "sport": self.sport,

            "league": self.league,

            "home_team": self.home_team,

            "away_team": self.away_team,

            "commence_time": self.commence_time.isoformat(),

            "bookmaker": self.bookmaker,

            "market": self.market,

            "status": self.status

        }
