"""
OddReal 2.0
Aplicação Principal
"""

from __future__ import annotations

import streamlit as st

from core.pipeline import pipeline
from pages import analysis
from pages import home
from pages import settings
from pages import valuebets


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="OddReal 2.0 | Central de Análise",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ESTADO DA APLICAÇÃO
# ============================================================

if "page" not in st.session_state:

    st.session_state["page"] = "Dashboard"


if "pipeline_data" not in st.session_state:

    st.session_state["pipeline_data"] = None


# ============================================================
# EXECUÇÃO DO PIPELINE
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def load_pipeline_data():

    return pipeline.execute()


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:

    data = load_pipeline_data()

    if not isinstance(data, dict):

        data = {}

except Exception as exc:

    data = {}

    st.error(
        "Não foi possível carregar os dados "
        "do sistema neste momento."
    )

    with st.expander(
        "Detalhes técnicos"
    ):

        st.exception(exc)


st.session_state[
    "pipeline_data"
] = data


# ============================================================
# DADOS
# ============================================================

events = data.get(
    "events",
    [],
)

analyses = data.get(
    "analyses",
    [],
)

value_bets = data.get(
    "value_bets",
    [],
)

best_match = data.get(
    "best_match",
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:10px 0 20px 0;
        ">
            <h1 style="
                margin:0;
                font-size:28px;
            ">
                ⚽ OddReal
            </h1>

            <p style="
                margin-top:5px;
                color:#64748b;
                font-size:13px;
            ">
                Central de Análise
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader(
        "Navegação"
    )

    page = st.radio(
        "Menu",
        [
            "Dashboard",
            "Análises",
            "Value Bets",
            "Configurações",
        ],
        key="main_navigation",
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "OddReal 2.0"
    )

    st.caption(
        "Motor quantitativo de análise "
        "de oportunidades."
    )

    st.divider()

    if st.button(
        "🔄 Atualizar dados",
        use_container_width=True,
    ):

        load_pipeline_data.clear()

        st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div style="
        padding:20px 24px;
        border-radius:16px;
        margin-bottom:24px;
        background:linear-gradient(
            135deg,
            #1E3A8A 0%,
            #3B82F6 100%
        );
        color:white;
        box-shadow:
            0 8px 24px
            rgba(15,23,42,0.12);
    ">

        <div style="
            font-size:28px;
            font-weight:700;
        ">
            OddReal 2.0
        </div>

        <div style="
            margin-top:5px;
            opacity:0.9;
            font-size:14px;
        ">
            Inteligência quantitativa para
            análise de oportunidades esportivas
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PÁGINAS
# ============================================================

if page == "Dashboard":

    home.render(
        data=data,
    )


elif page == "Análises":

    analysis.render(
        results=analyses,
    )


elif page == "Value Bets":

    valuebets.render(
        opportunities=value_bets,
    )


elif page == "Configurações":

    settings.render()
