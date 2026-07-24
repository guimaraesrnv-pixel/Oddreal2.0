import streamlit as st


def render():

    st.title("⚙️ Configurações")

    st.subheader("API")

    api_key = st.text_input(
        "The Odds API Key",
        type="password"
    )

    st.divider()

    st.subheader("Atualização")

    auto_refresh = st.toggle(
        "Atualização automática",
        value=True
    )

    refresh_time = st.slider(
        "Intervalo (segundos)",
        30,
        600,
        120
    )

    st.divider()

    st.subheader("Interface")

    theme = st.selectbox(
        "Tema",
        [
            "Claro",
            "Escuro",
            "Automático"
        ]
    )

    beginner = st.toggle(
        "Modo iniciante",
        value=True
    )

    explanations = st.toggle(
        "Mostrar explicações dos termos técnicos",
        value=True
    )

    st.divider()

    if st.button(
        "Salvar configurações",
        use_container_width=True
    ):

        st.success(
            "Configurações salvas com sucesso."
        )
