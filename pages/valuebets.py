import streamlit as st


def render(opportunities=None):

    st.title("💎 Value Bets")

    if not opportunities:

        st.warning(
            "Nenhuma Value Bet encontrada no momento."
        )

        return

    for value in opportunities:

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.subheader(
                    f"{value['home_team']} x {value['away_team']}"
                )

                st.write(
                    f"🎯 Probabilidade: {value['probability']}%"
                )

                st.write(
                    f"💰 EV: {value['expected_value']}%"
                )

            with col2:

                st.metric(
                    "Odd",
                    value["odd"]
                )

            st.success("✅ Oportunidade identificada pelo OddReal")

            if st.button(
                "Ver análise",
                key=value["event_id"]
            ):
                st.session_state["selected_event"] = value[
                    "event_id"
                ]
