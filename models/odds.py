from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Odds:
    """
    Modelo de odds de um evento.
    """

    bookmaker: str

    market: str

    home: Optional[float] = None

    draw: Optional[float] = None

    away: Optional[float] = None

    last_update: Optional[str] = None

    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:

        return {

            "bookmaker": self.bookmaker,

            "market": self.market,

            "home": self.home,

            "draw": self.draw,

            "away": self.away,

            "last_update": self.last_update,

            "metadata": self.metadata

        }
