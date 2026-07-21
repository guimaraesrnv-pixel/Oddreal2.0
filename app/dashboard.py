"""
OddReal 2.0

Arquivo:
app/dashboard.py

Painel visual do sistema.

Responsável por:
- Métricas
- Exibição de resultados
- Componentes do dashboard

Versão: 2.0
"""


import streamlit as st

from typing import Dict, Any, List



class Dashboard:
    """
    Gerenciador do painel visual.
    """



    def __init__(self):

        self.version = "2.0"

        self.name = "OddReal Dashboard"



    # ==================================================
    # CABEÇALHO
    # ==================================================

    def header(
        self
    ):
        """
        Exibe cabeçalho.
        """

        st.title(
            "⚽ OddReal 2.0"
        )


        st.caption(
            "Dashboard profissional de análise de odds"
        )



    # ==================================================
    # MÉTRICAS PRINCIPAIS
    # ==================================================

    def metrics(
        self,
        data: Dict[str, Any]
    ):
        """
        Exibe métricas.
        """

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(

                "Eventos",

                data.get(
                    "events",
                    0
                )

            )


        with col2:

            st.metric(

                "Análises",

                len(
                    data.get(
                        "results",
                        []
                    )
                )

            )


        with col3:

            st.metric(

                "Status",

                "OK"

            )
              # ==================================================
    # EXIBIR RESULTADOS
    # ==================================================

    def show_results(
        self,
        results: List[Dict[str, Any]]
    ):
        """
        Exibe resultados das análises.
        """

        st.subheader(
            "📈 Resultados das análises"
        )


        if not results:

            st.info(
                "Nenhum resultado encontrado."
            )

            return



        for index, result in enumerate(
            results
        ):

            with st.expander(
                f"Análise {index + 1}"
            ):

                st.json(
                    result
                )



    # ==================================================
    # EXIBIR VALUE BETS
    # ==================================================

    def show_value_bets(
        self,
        opportunities: List[Dict[str, Any]]
    ):
        """
        Mostra oportunidades de valor.
        """

        st.subheader(
            "💰 Value Bets"
        )


        if not opportunities:

            st.warning(
                "Nenhuma oportunidade encontrada."
            )

            return



        for item in opportunities:

            st.write(
                "Seleção:",
                item.get(
                    "selection",
                    ""
                )
            )


            st.write(
                "Odd:",
                item.get(
                    "odd",
                    0
                )
            )


            st.divider()



    # ==================================================
    # ALERTA DE STATUS
    # ==================================================

    def alert(
        self,
        message: str,
        status: str = "info"
    ):
        """
        Exibe alertas.
        """

        if status == "success":

            st.success(
                message
            )


        elif status == "error":

            st.error(
                message
            )


        elif status == "warning":

            st.warning(
                message
            )


        else:

            st.info(
                message
            )
    # ==================================================
    # STATUS DO DASHBOARD
    # ==================================================

    def status(
        self
    ) -> Dict[str, Any]:
        """
        Retorna informações do painel.
        """

        return {

            "module":

                "app.dashboard",


            "name":

                self.name,


            "version":

                self.version,


            "initialized":

                True

        }



    # ==================================================
    # CONFIGURAR PÁGINA
    # ==================================================

    def configure_page(
        self
    ):
        """
        Configura parâmetros visuais.
        """

        st.set_page_config(

            page_title="OddReal 2.0",

            page_icon="⚽",

            layout="wide"

        )



    # ==================================================
    # RENDER COMPLETO
    # ==================================================

    def render(
        self,
        data: Dict[str, Any]
    ):
        """
        Renderiza dashboard completo.
        """

        self.header()


        self.metrics(
            data
        )


        self.show_results(

            data.get(
                "results",
                []
            )

        )



    # ==================================================
    # LIMPAR CACHE VISUAL
    # ==================================================

    def clear(
        self
    ):
        """
        Limpa estado temporário.
        """

        st.cache_data.clear()



# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

dashboard = Dashboard()
