import streamlit as st

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

PAGES = {
    "🏠 Dashboard": home,
    "📈 Análises": analysis,
    "💎 Value Bets": valuebets,
    "⚙️ Configurações": settings,
}

st.sidebar.title("OddReal 2.0")

page = st.sidebar.radio(
    "Navegação",
    list(PAGES.keys())
)

PAGES[page].render()
