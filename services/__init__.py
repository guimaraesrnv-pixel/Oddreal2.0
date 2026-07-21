"""
OddReal 2.0

Pacote:
services

Serviços auxiliares do sistema.

Versão: 2.0
"""


# ======================================================
# IMPORTAÇÃO DOS SERVIÇOS
# ======================================================

from .cache import (

    CacheManager,

    cache_manager

)


from .api_client import (

    APIClient,

    api_client

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

    "api_client"

]
