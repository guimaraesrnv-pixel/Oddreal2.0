import streamlit as st


class Cards:
    """
    Componentes em formato de cartões.
    """

    @staticmethod
    def event_card(event):

        st.container()

        st.markdown(
            f"""
            ### {event.get('home_team')} x {event.get('away_team')}

            **Liga:** {event.get('league')}

            **Esporte:** {event.get('sport')}
            """
        )
