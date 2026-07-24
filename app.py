"""
OddReal 2.0
Aplicação Principal
"""

from __future__ import annotations

import streamlit as st

from core.pipeline import pipeline

from Pages import (
    home,
    analysis,
    valuebets,
    settings
)

st.set_page_config(
    page_title="OddReal 2.0",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# Carrega os dados do sistema
# ==========================================

data = pipeline.execute()

# ==========================================
# Sidebar
# ==========================================

st.sidebar.image(
    "assets/logo.png",
    use_container_width=True
)

st.sidebar.title("OddReal 2.0")

page = st.sidebar.radio(

    "Menu",

    [

        "Dashboard",

        "Análises",

        "Value Bets",

        "Configurações"

    ]

)

# ==========================================
# Navegação
# ==========================================

if page == "Dashboard":

    home.render(

        total_events=data["total_events"],

        total_valuebets=data["total_value_bets"],

        confidence=80,

        best_ev=12,

        last_update="Agora"

    )

elif page == "Análises":

    if data["analyses"]:

        analysis.render(

            data["analyses"][0]

        )

    else:

        analysis.render()

elif page == "Value Bets":

    valuebets.render(

        data["value_bets"]

    )

elif page == "Configurações":

    settings.render()
