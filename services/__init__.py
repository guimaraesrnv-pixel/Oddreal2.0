"""
OddReal 2.0

Pacote:
services

Camada de serviços do sistema.

Responsável por:
- API
- Cache
- Processamento de dados

Versão: 2.0
"""


# ======================================================
# CACHE
# ======================================================

from .cache import (

    CacheManager,

    cache_manager

)



# ======================================================
# API CLIENT
# ======================================================

from .api_client import (

    APIClient,

    api_client

)



# ======================================================
# DATA PROCESSOR
# ======================================================

from .data_processor import (

    DataProcessor,

    data_processor

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

    "CacheManager",

    "cache_manager",

    "APIClient",

    "api_client",

    "DataProcessor",

    "data_processor"

]
