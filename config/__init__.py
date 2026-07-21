"""
OddReal 2.0

Pacote:
oddsengine

Motor principal de análise de odds.

Responsável por:
- Cálculos
- Mercados
- Value Bets
- Probabilidades

Versão: 2.0
"""


# ======================================================
# IMPORTAÇÕES DO MOTOR
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

    MarketAnalyzer,

    market_analyzer

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

    "MarketAnalyzer",

    "market_analyzer",

    "ValueEngine",

    "value_engine"

]
