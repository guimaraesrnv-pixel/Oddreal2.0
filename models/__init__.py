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
    home_team: str
    away_team: str
    commence_time: datetime

    league: Optional[str] = None

    status: str = "scheduled"
