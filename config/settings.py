"""
OddReal 2.0

Módulo:
config/settings.py

Configurações gerais do sistema.

Responsável por:
- Nome do projeto
- Versão
- Ambiente
- Parâmetros globais

Versão: 2.0
"""


from typing import Dict, Any

from datetime import datetime



class Settings:
    """
    Configuração central do OddReal.
    """



    def __init__(self):

        self.name = "OddReal"


        self.version = "2.0"


        self.environment = "production"


        self.debug = False


        self.created_at = datetime.now()



    # ==================================================
    # INFORMAÇÕES DO SISTEMA
    # ==================================================

    def system_info(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações básicas.
        """

        return {

            "name":

                self.name,


            "version":

                self.version,


            "environment":

                self.environment,


            "debug":

                self.debug,


            "created_at":

                self.created_at.isoformat()

        }



    # ==================================================
    # ALTERAR AMBIENTE
    # ==================================================

    def set_environment(
        self,
        environment: str
    ) -> None:
        """
        Define ambiente de execução.
        """

        self.environment = environment



    # ==================================================
    # ATIVAR DEBUG
    # ==================================================

    def enable_debug(
        self
    ) -> None:
        """
        Ativa modo debug.
        """

        self.debug = True
      
    # ==================================================
    # CONFIGURAÇÕES DE ANÁLISE
    # ==================================================

    def analysis_config(
        self
    ) -> Dict[str, Any]:
        """
        Retorna parâmetros de análise.
        """

        return {

            "minimum_value_edge":

                5.0,


            "minimum_confidence":

                70,


            "maximum_risk":

                50,


            "default_limit_entries":

                10,


            "enable_value_engine":

                True

        }



    # ==================================================
    # CONFIGURAÇÕES DE ODDS
    # ==================================================

    def odds_config(
        self
    ) -> Dict[str, Any]:
        """
        Parâmetros do motor de odds.
        """

        return {

            "decimal_format":

                True,


            "minimum_odd":

                1.20,


            "maximum_odd":

                20.0,


            "calculate_probability":

                True

        }



    # ==================================================
    # CONFIGURAÇÕES DE CACHE
    # ==================================================

    def cache_config(
        self
    ) -> Dict[str, Any]:
        """
        Configurações padrão de cache.
        """

        return {

            "enabled":

                True,


            "expiration_minutes":

                15,


            "auto_cleanup":

                True

        }



    # ==================================================
    # CONFIGURAÇÕES DE PROCESSAMENTO
    # ==================================================

    def processing_config(
        self
    ) -> Dict[str, Any]:
        """
        Parâmetros do processamento.
        """

        return {

            "normalize_data":

                True,


            "validate_response":

                True,


            "save_history":

                True

        }
          # ==================================================
    # CONFIGURAÇÕES DA INTERFACE
    # ==================================================

    def interface_config(
        self
    ) -> Dict[str, Any]:
        """
        Configurações visuais do sistema.
        """

        return {

            "app_title":

                "OddReal 2.0",


            "page_layout":

                "wide",


            "show_metrics":

                True,


            "show_debug":

                self.debug

        }



    # ==================================================
    # CONFIGURAÇÕES DE HISTÓRICO
    # ==================================================

    def history_config(
        self
    ) -> Dict[str, Any]:
        """
        Configurações de armazenamento
        de histórico.
        """

        return {

            "enabled":

                True,


            "max_records":

                10000,


            "save_analysis":

                True,


            "save_results":

                True

        }



    # ==================================================
    # CAMINHOS DO PROJETO
    # ==================================================

    def paths(
        self
    ) -> Dict[str, str]:
        """
        Retorna caminhos padrões.
        """

        return {

            "root":

                "OddReal_2.0",


            "services":

                "services",


            "engine":

                "oddsengine",


            "config":

                "config"

        }



    # ==================================================
    # CONFIGURAÇÕES GERAIS
    # ==================================================

    def all_settings(
        self
    ) -> Dict[str, Any]:
        """
        Retorna todas as configurações.
        """

        return {

            "system":

                self.system_info(),


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

                self.history_config()

        }
          # ==================================================
    # ATUALIZAR CONFIGURAÇÃO
    # ==================================================

    def update(
        self,
        key: str,
        value: Any
    ) -> bool:
        """
        Atualiza uma configuração simples.
        """

        if hasattr(
            self,
            key
        ):

            setattr(

                self,

                key,

                value

            )

            return True



        return False



    # ==================================================
    # VALIDAR CONFIGURAÇÕES
    # ==================================================

    def validate(
        self
    ) -> Dict[str, Any]:
        """
        Verifica se configurações
        básicas estão corretas.
        """

        errors = []


        if not self.name:

            errors.append(
                "Nome do sistema vazio"
            )



        if not self.version:

            errors.append(
                "Versão não definida"
            )



        if self.environment not in [

            "development",

            "testing",

            "production"

        ]:

            errors.append(
                "Ambiente inválido"
            )



        return {

            "valid":

                len(errors) == 0,


            "errors":

                errors

        }



    # ==================================================
    # REINICIAR PADRÕES
    # ==================================================

    def reset_defaults(
        self
    ) -> None:
        """
        Retorna configurações
        básicas ao padrão.
        """

        self.name = "OddReal"

        self.version = "2.0"

        self.environment = "production"

        self.debug = False



    # ==================================================
    # EXPORTAR CONFIGURAÇÃO
    # ==================================================

    def export(
        self
    ) -> Dict[str, Any]:
        """
        Exporta configuração atual.
        """

        return {

            "settings":

                self.all_settings(),


            "exported_at":

                datetime.now()
                .isoformat()

        }
          # ==================================================
    # MODO DE EXECUÇÃO
    # ==================================================

    def is_production(
        self
    ) -> bool:
        """
        Verifica se está em produção.
        """

        return (

            self.environment
            ==
            "production"

        )



    def is_debug(
        self
    ) -> bool:
        """
        Retorna estado do debug.
        """

        return self.debug



    # ==================================================
    # CONFIGURAÇÃO DE RECURSOS
    # ==================================================

    def resources(
        self
    ) -> Dict[str, Any]:
        """
        Configuração de recursos.
        """

        return {

            "max_threads":

                4,


            "timeout":

                30,


            "memory_cache":

                True,


            "auto_restart":

                False

        }



    # ==================================================
    # CONFIGURAÇÃO DE SEGURANÇA
    # ==================================================

    def security(
        self
    ) -> Dict[str, Any]:
        """
        Configurações básicas
        de segurança.
        """

        return {

            "hide_api_keys":

                True,


            "validate_inputs":

                True,


            "safe_mode":

                True

        }



    # ==================================================
    # RESUMO DA CONFIGURAÇÃO
    # ==================================================

    def summary(
        self
    ) -> Dict[str, Any]:
        """
        Resumo geral das configurações.
        """

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


            "resources":

                self.resources()

        }
          # ==================================================
    # STATUS DO MÓDULO
    # ==================================================

    def status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna status atual
        das configurações.
        """

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


            "created_at":

                self.created_at.isoformat()

        }



    # ==================================================
    # CARREGAMENTO COMPLETO
    # ==================================================

    def load(
        self
    ) -> Dict[str, Any]:
        """
        Carrega todas as configurações.
        """

        return self.all_settings()



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

settings = Settings()
