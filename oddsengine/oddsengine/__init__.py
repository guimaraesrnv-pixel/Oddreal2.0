
"""
OddReal 2.0

Pacote:
oddsengine

Centralizador dos motores
de análise de odds.

Versão: 2.0
"""


# ======================================================
# IMPORTAÇÃO DOS MÓDULOS PRINCIPAIS
# ======================================================

from .odds import (
    OddsEngine,
    odds_engine
)


from .calculator import (
    OddsCalculator,
    odds_calculator
)


from .markets import (
    MarketManager,
    market_manager
)


from .value import (
    ValueEngine,
    value_engine
)



# ======================================================
# INFORMAÇÕES DO PACOTE
# ======================================================

__version__ = "2.0"


__author__ = "OddReal"



# ======================================================
# EXPORTS PÚBLICOS
# ======================================================

__all__ = [

    "OddsEngine",

    "odds_engine",

    "OddsCalculator",

    "odds_calculator",

    "MarketManager",

    "market_manager",

    "ValueEngine",

    "value_engine"

]
