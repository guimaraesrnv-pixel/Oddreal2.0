"""
OddReal 2.0

Pacote:
config

Configurações centrais do sistema.

Responsável por:
- Configurações gerais
- Configurações da API
- Parâmetros globais

Versão: 2.0
"""


# ======================================================
# SETTINGS
# ======================================================

from .settings import (

    Settings,

    settings

)



# ======================================================
# API CONFIG
# ======================================================

from .api import (

    APIConfig,

    api_config

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

    "Settings",

    "settings",

    "APIConfig",

    "api_config"

]
