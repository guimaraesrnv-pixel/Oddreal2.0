"""
OddReal 2.0

Módulo:
config/settings.py

Configuração central do sistema.

Responsável por:
- Configurações gerais;
- Configurações da The Odds API;
- Parâmetros de análise;
- Cache;
- Processamento;
- Interface;
- Histórico;
- Segurança;
- Recursos do sistema.

As informações sensíveis, principalmente a API Key,
devem ser obtidas por variável de ambiente ou
Streamlit Secrets.

Versão: 2.0
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

import streamlit as st


class Settings:
    """
    Configuração central do OddReal 2.0.
    """

    def __init__(self) -> None:

        # ==================================================
        # SISTEMA
        # ==================================================

        self.name = "OddReal"

        self.version = "2.0"

        self.environment = os.getenv(
            "ODDREAL_ENVIRONMENT",
            "production",
        )

        self.debug = (
            os.getenv(
                "ODDREAL_DEBUG",
                "false",
            ).lower()
            == "true"
        )

        self.created_at = datetime.now()

        # ==================================================
        # THE ODDS API
        # ==================================================

        self.api_key = self._load_api_key()

        self.base_url = os.getenv(
            "ODDS_API_BASE_URL",
            "https://api.the-odds-api.com/v4",
        ).rstrip("/")

        self.sport = os.getenv(
            "ODDS_API_SPORT",
            "soccer",
        )

        self.regions = os.getenv(
            "ODDS_API_REGIONS",
            "us",
        )

        self.markets = os.getenv(
            "ODDS_API_MARKETS",
            "h2h",
        )

        self.odds_format = os.getenv(
            "ODDS_API_FORMAT",
            "decimal",
        )

        # ==================================================
        # CONFIGURAÇÕES DE ANÁLISE
        # ==================================================

        self.minimum_value_edge = 5.0

        self.minimum_confidence = 70

        self.maximum_risk = 50

        self.default_limit_entries = 10

        self.enable_value_engine = True

        # ==================================================
        # CACHE
        # ==================================================

        self.cache_enabled = True

        self.cache_expiration_minutes = 15

        self.cache_auto_cleanup = True

        # ==================================================
        # PROCESSAMENTO
        # ==================================================

        self.normalize_data = True

        self.validate_response = True

        self.save_history = True

        # ==================================================
        # HISTÓRICO
        # ==================================================

        self.history_enabled = True

        self.history_max_records = 10000

        self.save_analysis = True

        self.save_results = True

        # ==================================================
        # RECURSOS
        # ==================================================

        self.max_threads = 4

        self.timeout = 30

        self.memory_cache = True

        self.auto_restart = False

        # ==================================================
        # SEGURANÇA
        # ==================================================

        self.hide_api_keys = True

        self.validate_inputs = True

        self.safe_mode = True

    # ======================================================
    # API KEY
    # ======================================================

    @staticmethod
    def _load_api_key() -> str:
        """
        Carrega a chave da The Odds API.

        Prioridade:

        1. Streamlit Secrets;
        2. Variável de ambiente.

        A chave nunca é exibida pelo módulo.
        """

        # --------------------------------------------------
        # STREAMLIT SECRETS
        # --------------------------------------------------

        try:

            secrets_key = st.secrets.get(
                "ODDS_API_KEY",
                "",
            )

            if secrets_key:

                return str(
                    secrets_key
                ).strip()

        except Exception:
            pass

        # --------------------------------------------------
        # VARIÁVEL DE AMBIENTE
        # --------------------------------------------------

        environment_key = os.getenv(
            "ODDS_API_KEY",
            "",
        )

        return str(
            environment_key
        ).strip()

    # ======================================================
    # INFORMAÇÕES DO SISTEMA
    # ======================================================

    def system_info(
        self,
    ) -> Dict[str, Any]:

        return {

            "name": self.name,

            "version": self.version,

            "environment": self.environment,

            "debug": self.debug,

            "created_at":
                self.created_at.isoformat(),

        }

    # ======================================================
    # CONFIGURAÇÕES DA API
    # ======================================================

    def api_config(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna configurações da API.

        A chave é mascarada.
        """

        masked_key = ""

        if self.api_key:

            if len(self.api_key) <= 8:

                masked_key = "********"

            else:

                masked_key = (
                    self.api_key[:4]
                    + "..."
                    + self.api_key[-4:]
                )

        return {

            "configured":
                bool(self.api_key),

            "api_key":
                masked_key,

            "base_url":
                self.base_url,

            "sport":
                self.sport,

            "regions":
                self.regions,

            "markets":
                self.markets,

            "odds_format":
                self.odds_format,

        }

    # ======================================================
    # CONFIGURAÇÕES DE ANÁLISE
    # ======================================================

    def analysis_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "minimum_value_edge":
                self.minimum_value_edge,

            "minimum_confidence":
                self.minimum_confidence,

            "maximum_risk":
                self.maximum_risk,

            "default_limit_entries":
                self.default_limit_entries,

            "enable_value_engine":
                self.enable_value_engine,

        }

    # ======================================================
    # CONFIGURAÇÕES DE ODDS
    # ======================================================

    def odds_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "decimal_format":
                self.odds_format == "decimal",

            "minimum_odd":
                1.20,

            "maximum_odd":
                20.0,

            "calculate_probability":
                True,

        }

    # ======================================================
    # CACHE
    # ======================================================

    def cache_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "enabled":
                self.cache_enabled,

            "expiration_minutes":
                self.cache_expiration_minutes,

            "auto_cleanup":
                self.cache_auto_cleanup,

        }

    # ======================================================
    # PROCESSAMENTO
    # ======================================================

    def processing_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "normalize_data":
                self.normalize_data,

            "validate_response":
                self.validate_response,

            "save_history":
                self.save_history,

        }

    # ======================================================
    # INTERFACE
    # ======================================================

    def interface_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "app_title":
                "OddReal 2.0",

            "page_layout":
                "wide",

            "show_metrics":
                True,

            "show_debug":
                self.debug,

        }

    # ======================================================
    # HISTÓRICO
    # ======================================================

    def history_config(
        self,
    ) -> Dict[str, Any]:

        return {

            "enabled":
                self.history_enabled,

            "max_records":
                self.history_max_records,

            "save_analysis":
                self.save_analysis,

            "save_results":
                self.save_results,

        }

    # ======================================================
    # CAMINHOS
    # ======================================================

    def paths(
        self,
    ) -> Dict[str, str]:

        return {

            "root":
                "OddReal_2.0",

            "services":
                "services",

            "engine":
                "oddsengine",

            "config":
                "config",

        }

    # ======================================================
    # RECURSOS
    # ======================================================

    def resources(
        self,
    ) -> Dict[str, Any]:

        return {

            "max_threads":
                self.max_threads,

            "timeout":
                self.timeout,

            "memory_cache":
                self.memory_cache,

            "auto_restart":
                self.auto_restart,

        }

    # ======================================================
    # SEGURANÇA
    # ======================================================

    def security(
        self,
    ) -> Dict[str, Any]:

        return {

            "hide_api_keys":
                self.hide_api_keys,

            "validate_inputs":
                self.validate_inputs,

            "safe_mode":
                self.safe_mode,

        }

    # ======================================================
    # TODAS AS CONFIGURAÇÕES
    # ======================================================

    def all_settings(
        self,
    ) -> Dict[str, Any]:

        return {

            "system":
                self.system_info(),

            "api":
                self.api_config(),

            "analysis":
                self.analysis_config(),

            "odds":
                self.odds_config(),

            "cache":
                self.cache_config(),

            "processing":
                self.processing_config(),

            "interface":
                self.interface_config(),

            "history":
                self.history_config(),

            "resources":
                self.resources(),

            "security":
                self.security(),

        }

    # ======================================================
    # ATUALIZAÇÃO
    # ======================================================

    def update(
        self,
        key: str,
        value: Any,
    ) -> bool:

        if not hasattr(
            self,
            key,
        ):

            return False

        setattr(
            self,
            key,
            value,
        )

        return True

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    def validate(
        self,
    ) -> Dict[str, Any]:

        errors = []

        if not self.name:

            errors.append(
                "Nome do sistema vazio."
            )

        if not self.version:

            errors.append(
                "Versão não definida."
            )

        if self.environment not in (
            "development",
            "testing",
            "production",
        ):

            errors.append(
                "Ambiente inválido."
            )

        if not self.base_url:

            errors.append(
                "URL da API não configurada."
            )

        if not self.api_key:

            errors.append(
                "Chave da The Odds API não configurada."
            )

        if self.odds_format not in (
            "decimal",
            "american",
        ):

            errors.append(
                "Formato de odds inválido."
            )

        return {

            "valid":
                len(errors) == 0,

            "errors":
                errors,

        }

    # ======================================================
    # PADRÕES
    # ======================================================

    def reset_defaults(
        self,
    ) -> None:

        self.name = "OddReal"

        self.version = "2.0"

        self.environment = "production"

        self.debug = False

        self.sport = "soccer"

        self.regions = "us"

        self.markets = "h2h"

        self.odds_format = "decimal"

        self.minimum_value_edge = 5.0

        self.minimum_confidence = 70

        self.maximum_risk = 50

    # ======================================================
    # EXPORTAÇÃO
    # ======================================================

    def export(
        self,
    ) -> Dict[str, Any]:

        return {

            "settings":
                self.all_settings(),

            "exported_at":
                datetime.now().isoformat(),

        }

    # ======================================================
    # ESTADO
    # ======================================================

    def is_production(
        self,
    ) -> bool:

        return (
            self.environment
            == "production"
        )

    def is_debug(
        self,
    ) -> bool:

        return self.debug

    # ======================================================
    # RESUMO
    # ======================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        return {

            "system":
                self.name,

            "version":
                self.version,

            "environment":
                self.environment,

            "debug":
                self.debug,

            "production":
                self.is_production(),

            "api_configured":
                bool(self.api_key),

            "sport":
                self.sport,

            "markets":
                self.markets,

            "resources":
                self.resources(),

        }

    # ======================================================
    # STATUS
    # ======================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "module":
                "config.settings",

            "service":
                "settings",

            "version":
                self.version,

            "initialized":
                True,

            "environment":
                self.environment,

            "api_configured":
                bool(self.api_key),

            "created_at":
                self.created_at.isoformat(),

        }

    # ======================================================
    # CARREGAMENTO
    # ======================================================

    def load(
        self,
    ) -> Dict[str, Any]:

        return self.all_settings()


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

settings = Settings()
