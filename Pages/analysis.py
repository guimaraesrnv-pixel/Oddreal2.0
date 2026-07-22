
import streamlit as st


def render(results=None):
    """
    Página de análises.
    """

    st.title("📊 Análise de Jogos")

    if not results:
        st.info("Nenhuma análise disponível.")
        return

    st.subheader("Resultados")

    for index, result in enumerate(results):

        with st.expander(f"Jogo {index + 1}"):

            st.json(result)
