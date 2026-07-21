"""
OddReal 2.0

Módulo:
core/pipeline.py

Pipeline principal do sistema.

Responsável por:
- Orquestrar fluxo de dados
- Integrar serviços
- Executar análises

Versão: 2.0
"""


from typing import Dict, Any, List

from datetime import datetime



class Pipeline:
    """
    Controlador principal do fluxo.
    """



    def __init__(self):

        self.version = "2.0"

        self.name = "OddReal Pipeline"

        self.created_at = datetime.now()

        self.history = []



    # ==================================================
    # VALIDAR DADOS
    # ==================================================

    def validate(
        self,
        data: Any
    ) -> bool:
        """
        Valida entrada do pipeline.
        """

        if data is None:

            return False



        if isinstance(
            data,
            (dict, list)
        ):

            return len(data) > 0



        return False



    # ==================================================
    # REGISTRAR EXECUÇÃO
    # ==================================================

    def register(
        self,
        step: str,
        status: bool
    ) -> Dict[str, Any]:
        """
        Registra etapa executada.
        """

        record = {

            "step":

                step,


            "success":

                status,


            "time":

                datetime.now()
                .isoformat()

        }


        self.history.append(
            record
        )


        return record



    # ==================================================
    # INICIAR PIPELINE
    # ==================================================

    def start(
        self
    ) -> Dict[str, Any]:
        """
        Inicia execução.
        """

        return {

            "pipeline":

                self.name,


            "version":

                self.version,


            "started":

                datetime.now()
                .isoformat()

        }

    # ==================================================
    # BUSCAR DADOS DA API
    # ==================================================

    def fetch_data(
        self,
        api_client,
        sport: str
    ) -> Dict[str, Any]:
        """
        Busca eventos através da API.
        """

        try:

            response = api_client.cached_events(

                sport

            )


            self.register(

                "api_fetch",

                response.get(
                    "success",
                    False
                )

            )


            return response



        except Exception as error:

            self.register(

                "api_fetch",

                False

            )


            return {

                "success":

                    False,


                "error":

                    str(error)

            }



    # ==================================================
    # PROCESSAR DADOS
    # ==================================================

    def process_data(
        self,
        response: Dict[str, Any],
        processor
    ) -> List[Dict[str, Any]]:
        """
        Processa retorno da API.
        """

        try:

            events = processor.run(

                response

            )


            self.register(

                "data_processing",

                True

            )


            return events



        except Exception:

            self.register(

                "data_processing",

                False

            )


            return []



    # ==================================================
    # EXECUTAR ANÁLISE
    # ==================================================

    def execute_analysis(
        self,
        events: List[Dict[str, Any]],
        analyzer,
        odds_engine
    ) -> List[Dict[str, Any]]:
        """
        Executa análise dos eventos.
        """

        if not events:

            return []



        results = analyzer.analyze_batch(

            events,

            odds_engine

        )


        self.register(

            "analysis",

            True

        )


        return results



    # ==================================================
    # EXECUÇÃO COMPLETA
    # ==================================================

    def run(
        self,
        sport: str,
        api_client,
        processor,
        analyzer,
        odds_engine
    ) -> Dict[str, Any]:
        """
        Executa pipeline completo.
        """

        self.start()


        response = self.fetch_data(

            api_client,

            sport

        )


        events = self.process_data(

            response,

            processor

        )


        results = self.execute_analysis(

            events,

            analyzer,

            odds_engine

        )


        return {

            "success":

                True,


            "events":

                len(events),


            "results":

                results,


            "history":

                self.history

        }
          # ==================================================
    # STATUS DO PIPELINE
    # ==================================================

    def status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do pipeline.
        """

        return {

            "module":

                "core.pipeline",


            "name":

                self.name,


            "version":

                self.version,


            "executions":

                len(
                    self.history
                ),


            "initialized":

                True

        }



    # ==================================================
    # ÚLTIMA EXECUÇÃO
    # ==================================================

    def last_execution(
        self
    ) -> Dict[str, Any]:
        """
        Retorna último registro.
        """

        if not self.history:

            return {}


        return self.history[-1]



    # ==================================================
    # LIMPAR HISTÓRICO
    # ==================================================

    def clear_history(
        self
    ) -> None:
        """
        Remove histórico temporário.
        """

        self.history = []



    # ==================================================
    # EXPORTAR ESTADO
    # ==================================================

    def export(
        self
    ) -> Dict[str, Any]:
        """
        Exporta estado atual.
        """

        return {

            "pipeline":

                self.name,


            "version":

                self.version,


            "history":

                self.history,


            "exported_at":

                datetime.now()
                .isoformat()

        }



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

pipeline = Pipeline()
