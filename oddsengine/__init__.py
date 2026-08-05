
"""
"""
OddReal 2.0
Odds Engine

Pacote responsável pelos motores matemáticos
e estatísticos relacionados às odds.

Os motores são independentes da interface,
da API e da IA.
"""

from .value import (
    ValueBetEngine,
    valuebet_engine,
)

__all__ = [
    "ValueBetEngine",
    "valuebet_engine",
]
