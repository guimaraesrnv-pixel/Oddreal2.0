"""
OddReal 2.0

Arquivo:
app/main.py

Entrada principal do Streamlit.

Responsável por:
- Inicializar aplicação
- Carregar configurações
- Conectar módulos

Versão: 2.0
"""


import streamlit as st


from config import (

    settings,

    api_config

)


from core import (

    pipeline,

    analyzer

)



# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================

st.set_page_config(

    page_title="OddReal 2.0",

    page_icon="⚽",

    layout="wide"

)



# ======================================================
# INICIALIZAÇÃO
# ======================================================

def initialize():

    """
    Inicializa o sistema.
    """

    return {

        "settings":

            settings,


        "api":

            api_config,


        "pipeline":

            pipeline,


        "analyzer":

            analyzer

    }



# Carregar sistema

system = initialize()



# ======================================================
# CABEÇALHO
# ======================================================

st.title(
    "⚽ OddReal 2.0"
)


st.caption(
    "Sistema profissional de análise de odds e value bets"
)
# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:

    st.header(
        "⚙️ Configurações"
    )


    st.write(
        "Versão:",
        settings.version
    )


    st.write(
        "Ambiente:",
        settings.environment
    )


    st.divider()


    st.subheader(
        "API"
    )


    api_status = api_config.status()


    if api_status["configured"]:

        st.success(
            "API configurada"
        )

    else:

        st.warning(
            "API Key não configurada"
        )



# ======================================================
# STATUS DO SISTEMA
# ======================================================

st.subheader(
    "📊 Status do Sistema"
)


col1, col2, col3 = st.columns(3)



with col1:

    st.metric(

        "Config",

        "OK"

    )



with col2:

    st.metric(

        "Pipeline",

        "Ativo"

    )



with col3:

    st.metric(

        "Engine",

        "Online"

    )



# ======================================================
# ÁREA PRINCIPAL
# ======================================================

st.divider()


st.subheader(
    "🔎 Análise de Jogos"
)


sport = st.selectbox(

    "Escolha o esporte",

    [

        "soccer",

        "basketball",

        "tennis"

    ]
  

)
# ======================================================
# EXECUTAR ANÁLISE
# ======================================================

if st.button(
    "🚀 Executar análise"
):

    with st.spinner(
        "Analisando jogos..."
    ):

        try:

            result = pipeline.run(

                sport,

                system["api"],

                __import__(
                    "services",
                    fromlist=[
                        "data_processor"
                    ]
                ).data_processor,

                system["analyzer"],

                __import__(
                    "oddsengine",
                    fromlist=[
                        "odds_engine"
                    ]
                ).odds_engine

            )


            st.success(
                "Análise concluída"
            )


            st.write(
                "Eventos encontrados:",
                result.get(
                    "events",
                    0
                )
            )


            st.subheader(
                "Resultados"
            )


            st.json(
                result.get(
                    "results",
                    []
                )
            )



        except Exception as error:

            st.error(
                f"Erro na análise: {error}"
            )



# ======================================================
# RODAPÉ
# ======================================================

st.divider()


st.caption(
    "OddReal 2.0 © Sistema inteligente de análise de odds"
)
