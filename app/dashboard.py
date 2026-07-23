import streamlit as st


class Dashboard:

    @staticmethod
    def configure_page():
        st.set_page_config(
            page_title="OddReal 2.0",
            page_icon="⚽",
            layout="wide"
        )

    @staticmethod
    def header():
        st.title("⚽ OddReal 2.0")
        st.caption("Central Inteligente de Análise de Odds")

    @staticmethod
    def metrics(total_events, total_valuebets):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Eventos", total_events)

        with col2:
            st.metric("Value Bets", total_valuebets)

    @staticmethod
    def render(data):

        Dashboard.header()

        total_events = data.get("events", 0)

        results = data.get("results", [])

        Dashboard.metrics(
            total_events,
            len(results)
        )

        if results:

            st.subheader("Resultados")

            st.json(results)


dashboard = Dashboard()
