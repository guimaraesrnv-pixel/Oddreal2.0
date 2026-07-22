
import streamlit as st


def render():
    """
    Página de configurações.
    """

    st.title("⚙️ Configurações")

    st.write("Configurações do sistema OddReal 2.0")

    st.checkbox("Atualização automática", value=True)

    st.checkbox("Modo escuro", value=False)
