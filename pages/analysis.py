import streamlit as st


def render(analysis=None):

    st.title("📈 Análise da Partida")

    if analysis is None:

        st.info("Selecione um jogo para visualizar a análise.")

        return

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏠 Mandante")
        st.write(analysis.get("home_team", "-"))

        st.subheader("🚩 Visitante")
        st.write(analysis.get("away_team", "-"))

        st.subheader("⭐ Índice OddReal")
        st.progress(
            analysis.get("confidence", 0) / 100
        )

        st.metric(
            "Confiança",
            f'{analysis.get("confidence",0)}%'
        )

    with col2:

        best = analysis.get("best_odd", {})

        st.metric(
            "Melhor Odd",
            best.get("odd", "-")
        )

        st.metric(
            "Casa",
            best.get("bookmaker", "-")
        )

        st.metric(
            "Equipe",
            best.get("team", "-")
        )

    st.divider()

    st.subheader("🤖 Explicação da IA")

    st.info(

        analysis.get(

            "explanation",

            "A análise será gerada automaticamente pelo AI Engine."

        )

    )

    st.divider()

    st.subheader("📊 Resumo")

    st.json(analysis)
