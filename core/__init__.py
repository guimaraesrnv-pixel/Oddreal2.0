"""
OddReal 2.0

Pacote:
core

Camada central de integração.

Responsável por:
- Orquestração
- Pipeline
- Análises

Versão: 2.0
"""


# ======================================================
# ANALYZER
# ======================================================

from .analyzer import (

    Analyzer,

    analyzer

)



# ======================================================
# PIPELINE
# ======================================================

from .pipeline import (

    Pipeline,

    pipeline

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

    "Analyzer",

    "analyzer",

    "Pipeline",

    "pipeline"

]
