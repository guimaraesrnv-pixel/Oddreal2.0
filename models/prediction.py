from dataclasses import dataclass
from typing import Optional


@dataclass
class Prediction:
    """
    Resultado de uma análise.
    """

    event_id: str

    market: str

    selection: str

    probability: float

    implied_probability: float

    expected_value: float

    confidence: float

    recommended: bool = False

    notes: Optional[str] = None
