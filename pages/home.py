import streamlit as st


def render(
    total_events=0,
    total_valuebets=0,
    confidence=0,
    best_ev=0,
    last_update="--:--"
):
    st.title("⚽ OddReal 2.0")
    st.caption("Central Inteligente de Análise Esportiva")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("⚽ Jogos", total_events)
    c2.metric("💎 Value Bets", total_valuebets)
    c3.metric("🎯 Confiança Média", f"{confidence}%")
    c4.metric("🔥 Melhor EV", f"{best_ev}%")

    st.divider()

    st.subheader("📊 Radar OddReal")

    st.info(
        "Os jogos com maior Índice OddReal aparecerão aqui "
        "automaticamente após a análise."
    )

    st.divider()

    st.subheader("💎 Oportunidades do Dia")

    st.write(
        "Nenhuma oportunidade disponível no momento."
    )

    st.divider()

    st.subheader("🚨 Alertas")

    st.success("Sistema funcionando normalmente.")

    st.caption(f"Última atualização: {last_update}")
