
import streamlit as st


def render():
    """
    Página inicial do OddReal.
    """

    st.title("⚽ OddReal 2.0")

    st.subheader("Bem-vindo!")

    st.write(
        """
        O OddReal é uma plataforma de análise inteligente
        de apostas esportivas.

        Utilize o menu lateral para navegar entre as
        funcionalidades do sistema.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Eventos", "0")

    with col2:
        st.metric("Value Bets", "0")

    with col3:
        st.metric("ROI", "0%")
