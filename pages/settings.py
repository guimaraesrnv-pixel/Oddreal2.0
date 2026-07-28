"""
OddReal 2.0
Página de Configurações
"""

from __future__ import annotations

import streamlit as st


def _initialize_settings() -> None:
    """Inicializa as configurações da aplicação."""

    defaults = {
        "auto_refresh": True,
        "refresh_interval": 5,
        "show_only_value_bets": False,
        "minimum_oddreal_index": 55,
        "minimum_expected_value": 5.0,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


def render() -> None:
    """Renderiza a página de configurações."""

    _initialize_settings()

    st.title("⚙️ Configurações")

    st.caption(
        "Configure como o OddReal apresenta e filtra "
        "as oportunidades analisadas."
    )

    st.subheader("🔄 Atualização dos dados")

    auto_refresh = st.toggle(
        "Atualização automática",
        value=st.session_state["auto_refresh"],
        help=(
            "Permite atualizar os dados periodicamente. "
            "A atualização automática será integrada ao "
            "mecanismo de coleta em uma etapa posterior."
        ),
    )

    st.session_state["auto_refresh"] = auto_refresh

    refresh_interval = st.select_slider(
        "Intervalo de atualização",
        options=[1, 3, 5, 10, 15, 30],
        value=st.session_state["refresh_interval"],
        format_func=lambda value: f"{value} minutos",
        disabled=not auto_refresh,
    )

    st.session_state["refresh_interval"] = refresh_interval

    st.divider()

    st.subheader("🎯 Filtros de oportunidades")

    show_only_value_bets = st.toggle(
        "Mostrar somente Value Bets",
        value=st.session_state[
            "show_only_value_bets"
        ],
        help=(
            "Quando ativado, a interface prioriza "
            "oportunidades classificadas como Value Bet."
        ),
    )

    st.session_state[
        "show_only_value_bets"
    ] = show_only_value_bets

    minimum_index = st.slider(
        "Índice OddReal mínimo",
        min_value=0,
        max_value=100,
        value=st.session_state[
            "minimum_oddreal_index"
        ],
        step=5,
        help=(
            "Define o índice mínimo utilizado "
            "como referência para oportunidades."
        ),
    )

    st.session_state[
        "minimum_oddreal_index"
    ] = minimum_index

    minimum_ev = st.number_input(
        "EV mínimo (%)",
        min_value=-100.0,
        max_value=100.0,
        value=float(
            st.session_state[
                "minimum_expected_value"
            ]
        ),
        step=0.5,
        format="%.2f",
        help=(
            "EV significa Valor Esperado. "
            "Ele representa o retorno matemático "
            "estimado de uma oportunidade."
        ),
    )

    st.session_state[
        "minimum_expected_value"
    ] = minimum_ev

    st.divider()

    st.subheader("📚 Termos técnicos")

    with st.expander(
        "O que é EV?"
    ):

        st.write(
            """
            **EV — Expected Value (Valor Esperado)**

            É uma estimativa matemática usada para avaliar
            se uma determinada odd apresenta valor em relação
            à probabilidade considerada pelo modelo.

            EV positivo não significa que um resultado
            específico irá acontecer. Ele representa apenas
            uma vantagem matemática estimada.
            """
        )

    with st.expander(
        "O que é o Índice OddReal?"
    ):

        st.write(
            """
            O **Índice OddReal** é uma pontuação interna
            utilizada pelo sistema para combinar diferentes
            indicadores da análise.

            Quanto maior a pontuação, maior é a classificação
            da oportunidade segundo os critérios atuais
            do motor.

            A pontuação não representa garantia de resultado.
            """
        )

    with st.expander(
        "O que é Value Bet?"
    ):

        st.write(
            """
            **Value Bet** significa uma oportunidade em que
            a avaliação matemática do sistema indica que a
            odd pode estar acima do valor considerado justo
            pela probabilidade estimada.

            Isso não significa aposta garantida.
            """
        )

    with st.expander(
        "O que é risco?"
    ):

        st.write(
            """
            O nível de risco é uma classificação interna
            baseada nos indicadores disponíveis.

            Ele serve para facilitar a leitura da análise
            e não representa uma previsão certa do resultado.
            """
        )

    st.divider()

    st.subheader("💾 Estado atual")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Atualização automática",
            "Ativa"
            if st.session_state["auto_refresh"]
            else "Desativada",
        )

    with col2:

        st.metric(
            "Índice mínimo",
            st.session_state[
                "minimum_oddreal_index"
            ],
        )

    with col3:

        st.metric(
            "EV mínimo",
            f"{st.session_state['minimum_expected_value']:.2f}%",
        )

    st.info(
        "As configurações ficam armazenadas na sessão "
        "atual do Streamlit. A persistência definitiva "
        "será integrada posteriormente ao sistema de "
        "configuração do OddReal."
    )
