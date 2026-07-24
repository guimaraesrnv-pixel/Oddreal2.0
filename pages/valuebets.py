
import streamlit as st


def render(opportunities=None):
    """
    Página de Value Bets.
    """

    st.title("💰 Value Bets")

    if not opportunities:
        st.warning("Nenhuma oportunidade encontrada.")
        return

    for value in opportunities:

        st.write(value)
