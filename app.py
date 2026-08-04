"""
OddReal 2.0
Central de Análise de Odds

Interface principal Streamlit.

Fluxo:

API
 ↓
DataManager
 ↓
Pipeline
 ↓
Analyzer
 ↓
OddsEngine
 ↓
AIEngine
 ↓
Dashboard
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from core.pipeline import pipeline
from modules.ai_engine import ai_engine
from modules.logger import info


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="OddReal 2.0 | Central de Análise de Odds",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    .oddreal-header {
        background:
            linear-gradient(
                135deg,
                #1E3A8A 0%,
                #3B82F6 100%
            );

        padding: 24px 30px;

        border-radius: 18px;

        color: white;

        margin-bottom: 24px;

        box-shadow:
            0 10px 30px
            rgba(30, 58, 138, 0.18);
    }

    .oddreal-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
    }

    .oddreal-header p {
        margin: 7px 0 0 0;
        opacity: 0.90;
        font-size: 1rem;
    }

    .metric-card {
        background: white;

        border: 1px solid #E2E8F0;

        border-radius: 16px;

        padding: 20px;

        min-height: 125px;

        box-shadow:
            0 5px 18px
            rgba(15, 23, 42, 0.05);
    }

    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .metric-value {
        color: #0F172A;
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: 8px;
    }

    .section-title {
        color: #0F172A;
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .analysis-card {
        background: white;

        border: 1px solid #E2E8F0;

        border-radius: 16px;

        padding: 20px;

        margin-bottom: 14px;

        box-shadow:
            0 4px 16px
            rgba(15, 23, 42, 0.04);
    }

    .badge {
        display: inline-block;

        padding: 5px 10px;

        border-radius: 999px;

        background: #EFF6FF;

        color: #1D4ED8;

        font-size: 0.78rem;

        font-weight: 700;
    }

    .positive {
        color: #15803D;
        font-weight: 800;
    }

    .negative {
        color: #B91C1C;
        font-weight: 800;
    }

    .muted {
        color: #64748B;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "pipeline_result" not in st.session_state:

    st.session_state[
        "pipeline_result"
    ] = None


if "ai_result" not in st.session_state:

    st.session_state[
        "ai_result"
    ] = None


if "page" not in st.session_state:

    st.session_state[
        "page"
    ] = "Dashboard"


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def money_or_number(
    value: Any,
) -> str:

    if value is None:

        return "0"

    try:

        return f"{float(value):.2f}"

    except (
        TypeError,
        ValueError,
    ):

        return "0"


def percentage(
    value: Any,
) -> str:

    if value is None:

        return "0%"

    try:

        return f"{float(value):.2f}%"

    except (
        TypeError,
        ValueError,
    ):

        return "0%"


def get_result() -> Dict[str, Any]:

    result = st.session_state.get(
        "pipeline_result"
    )

    if not isinstance(
        result,
        dict,
    ):

        return {}

    return result


def run_pipeline(
    force_refresh: bool = False,
) -> None:

    with st.spinner(
        "Atualizando eventos e analisando o mercado..."
    ):

        result = pipeline.execute(
            force_refresh=force_refresh
        )

    st.session_state[
        "pipeline_result"
    ] = result

    st.session_state[
        "ai_result"
    ] = None

    info(
        "Dashboard atualizado."
    )


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="oddreal-header">

        <h1>
            ⚽ OddReal 2.0
        </h1>

        <p>
            Central inteligente de análise de odds,
            Value Bets e inteligência de mercado.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVEGAÇÃO
# ============================================================

nav1, nav2, nav3, nav4 = st.columns(
    4
)


with nav1:

    if st.button(
        "📊 Dashboard",
        use_container_width=True,
    ):

        st.session_state[
            "page"
        ] = "Dashboard"


with nav2:

    if st.button(
        "🎯 Value Bets",
        use_container_width=True,
    ):

        st.session_state[
            "page"
        ] = "Value Bets"


with nav3:

    if st.button(
        "🤖 Inteligência IA",
        use_container_width=True,
    ):

        st.session_state[
            "page"
        ] = "IA"


with nav4:

    if st.button(
        "🔄 Atualizar Mercado",
        use_container_width=True,
    ):

        run_pipeline(
            force_refresh=True
        )

        st.rerun()


st.divider()


# ============================================================
# RESULTADO ATUAL
# ============================================================

result = get_result()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state[
    "page"
] == "Dashboard":

    st.markdown(
        '<div class="section-title">Visão geral do mercado</div>',
        unsafe_allow_html=True,
    )

    if not result:

        st.info(
            "Nenhum mercado foi carregado ainda."
        )

        if st.button(
            "🚀 Carregar mercado agora",
            type="primary",
            use_container_width=True,
        ):

            run_pipeline()

            st.rerun()

    else:

        total_events = result.get(
            "total_events",
            0,
        )

        total_analyses = result.get(
            "total_analyses",
            0,
        )

        total_value_bets = result.get(
            "total_value_bets",
            0,
        )

        summary = result.get(
            "analysis_summary",
            {},
        )

        average_index = summary.get(
            "average_index",
            0,
        )

        col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Eventos
            </div>
            <div class="metric-value">
                {total_events}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Análises
            </div>
            <div class="metric-value">
                {total_analyses}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Value Bets
            </div>
            <div class="metric-value">
                {total_value_bets}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Índice médio
            </div>
            <div class="metric-value">
                {money_or_number(average_index)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
        # ----------------------------------------------------
        # MELHOR OPORTUNIDADE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Melhor oportunidade</div>',
            unsafe_allow_html=True,
        )

        best = result.get(
            "best_match"
        )

        if best:

            home = best.get(
                "home_team",
                "Mandante",
            )

            away = best.get(
                "away_team",
                "Visitante",
            )

            odd = best.get(
                "odd",
                0,
            )

            ev = best.get(
                "expected_value",
                0,
            )

            index = best.get(
                "oddreal_index",
                0,
            )

            confidence = best.get(
                "confidence_level",
                "Baixa",
            )

            risk = best.get(
                "risk",
                "Alto",
            )

            st.markdown(
                f"""
                <div class="analysis-card">

                    <h3>
                        {home}
                        ×
                        {away}
                    </h3>

                    <p class="muted">
                        {best.get(
                            "selected_market",
                            "Mercado"
                        )}
                        —
                        {best.get(
                            "selected_outcome",
                            "Seleção"
                        )}
                    </p>

                    <hr>

                    <b>Odd:</b>
                    {money_or_number(odd)}

                    &nbsp;&nbsp;

                    <b>EV:</b>
                    <span class="positive">
                        {percentage(ev)}
                    </span>

                    &nbsp;&nbsp;

                    <b>Índice OddReal:</b>
                    {index}

                    &nbsp;&nbsp;

                    <b>Confiança:</b>
                    {confidence}

                    &nbsp;&nbsp;

                    <b>Risco:</b>
                    {risk}

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "Nenhuma oportunidade disponível."
            )

        # ----------------------------------------------------
        # ANÁLISES
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Análises recentes</div>',
            unsafe_allow_html=True,
        )

        analyses = result.get(
            "analyses",
            [],
        )

        if not analyses:

            st.warning(
                "Nenhuma análise foi encontrada."
            )

        else:

            for analysis in analyses[:15]:

                home = analysis.get(
                    "home_team",
                    "Mandante",
                )

                away = analysis.get(
                    "away_team",
                    "Visitante",
                )

                odd = analysis.get(
                    "odd",
                    0,
                )

                ev = analysis.get(
                    "expected_value",
                    0,
                )

                index = analysis.get(
                    "oddreal_index",
                    0,
                )

                is_value = analysis.get(
                    "is_value_bet",
                    False,
                )

                badge = (
                    "🎯 VALUE BET"
                    if is_value
                    else "Análise"
                )

                st.markdown(
                    f"""
                    <div class="analysis-card">

                        <span class="badge">
                            {badge}
                        </span>

                        <h4>
                            {home}
                            ×
                            {away}
                        </h4>

                        Odd:
                        <b>
                            {money_or_number(odd)}
                        </b>

                        &nbsp; | &nbsp;

                        EV:
                        <b class="{
                            'positive'
                            if ev > 0
                            else 'negative'
                        }">
                            {percentage(ev)}
                        </b>

                        &nbsp; | &nbsp;

                        Índice:
                        <b>
                            {index}
                        </b>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# VALUE BETS
# ============================================================

elif st.session_state[
    "page"
] == "Value Bets":

    st.markdown(
        '<div class="section-title">🎯 Value Bets</div>',
        unsafe_allow_html=True,
    )

    if not result:

        st.info(
            "Carregue o mercado primeiro."
        )

    else:

        value_bets = result.get(
            "value_bets",
            [],
        )

        if not value_bets:

            st.warning(
                "Nenhuma Value Bet encontrada "
                "com os critérios atuais."
            )

        else:

            st.success(
                f"{len(value_bets)} oportunidades "
                "encontradas."
            )

            for item in value_bets:

                home = item.get(
                    "home_team",
                    "Mandante",
                )

                away = item.get(
                    "away_team",
                    "Visitante",
                )

                odd = item.get(
                    "odd",
                    0,
                )

                ev = item.get(
                    "expected_value",
                    0,
                )

                probability = item.get(
                    "probability",
                    0,
                )

                index = item.get(
                    "oddreal_index",
                    0,
                )

                variation = item.get(
                    "market_variation",
                    0,
                )

                bookmaker = item.get(
                    "selected_bookmaker",
                    "Casa não informada",
                )

                st.markdown(
                    f"""
                    <div class="analysis-card">

                        <span class="badge">
                            🎯 VALUE BET
                        </span>

                        <h3>
                            {home}
                            ×
                            {away}
                        </h3>

                        <p class="muted">
                            {item.get(
                                "selected_market",
                                "Mercado"
                            )}
                            —
                            {item.get(
                                "selected_outcome",
                                "Seleção"
                            )}
                        </p>

                        <hr>

                        <b>Casa:</b>
                        {bookmaker}

                        &nbsp;&nbsp;

                        <b>Odd:</b>
                        {money_or_number(odd)}

                        &nbsp;&nbsp;

                        <b>Probabilidade:</b>
                        {percentage(probability)}

                        &nbsp;&nbsp;

                        <b>EV:</b>
                        <span class="positive">
                            {percentage(ev)}
                        </span>

                        <br><br>

                        <b>Índice OddReal:</b>
                        {index}

                        &nbsp;&nbsp;

                        <b>Variação de mercado:</b>
                        {percentage(variation)}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# IA
# ============================================================

elif st.session_state[
    "page"
] == "IA":

    st.markdown(
        '<div class="section-title">🤖 Inteligência Artificial</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        A inteligência do OddReal interpreta os indicadores
        matemáticos produzidos pelo motor quantitativo.

        Ela não altera odds, probabilidades ou EV.
        """
    )

    if not result:

        st.info(
            "Carregue o mercado antes de utilizar a IA."
        )

    else:

        analyses = result.get(
            "analyses",
            [],
        )

        if not analyses:

            st.warning(
                "Não existem análises disponíveis."
            )

        else:

            options = []

            for i, item in enumerate(
                analyses
            ):

                home = item.get(
                    "home_team",
                    "Mandante",
                )

                away = item.get(
                    "away_team",
                    "Visitante",
                )

                options.append(
                    f"{i + 1}. {home} × {away}"
                )

            selected = st.selectbox(
                "Selecione o evento para análise",
                options,
            )

            selected_index = options.index(
                selected
            )

            selected_analysis = analyses[
                selected_index
            ]

            st.markdown(
                "### Evento selecionado"
            )

            st.info(
                f"{selected_analysis.get('home_team', 'Mandante')} "
                f"× "
                f"{selected_analysis.get('away_team', 'Visitante')}"
            )

            if st.button(
                "🤖 Analisar com IA",
                type="primary",
                use_container_width=True,
            ):

                with st.spinner(
                    "A IA está interpretando os indicadores..."
                ):

                    ai_result = ai_engine.analyze(
                        selected_analysis
                    )

                st.session_state[
                    "ai_result"
                ] = ai_result

                st.rerun()

            ai_result = st.session_state.get(
                "ai_result"
            )

            if ai_result:

                if ai_result.get(
                    "status"
                ) == "success":

                    indicators = ai_result.get(
                        "indicators",
                        {},
                    )

                    st.markdown(
                        '<div class="section-title">Diagnóstico técnico</div>',
                        unsafe_allow_html=True,
                    )

                    col1, col2, col3, col4 = st.columns(
                        4
                    )

                    with col1:

                        st.metric(
                            "Odd",
                            money_or_number(
                                indicators.get(
                                    "odd"
                                )
                            ),
                        )

                    with col2:

                        st.metric(
                            "EV",
                            percentage(
                                indicators.get(
                                    "expected_value"
                                )
                            ),
                        )

                    with col3:

                        st.metric(
                            "Índice OddReal",
                            indicators.get(
                                "oddreal_index",
                                0,
                            ),
                        )

                    with col4:

                        st.metric(
                            "Risco",
                            indicators.get(
                                "risk",
                                "Alto",
                            ),
                        )

                    st.markdown(
                        "### 📊 Indicadores completos"
                    )

                    indicator_col1, indicator_col2 = st.columns(
                        2
                    )

                    with indicator_col1:

                        st.write(
                            "**Probabilidade:** "
                            + percentage(
                                indicators.get(
                                    "probability"
                                )
                            )
                        )

                        st.write(
                            "**Confiança:** "
                            + str(
                                indicators.get(
                                    "confidence_level",
                                    "Não informado",
                                )
                            )
                        )

                        st.write(
                            "**Odd média do mercado:** "
                            + money_or_number(
                                indicators.get(
                                    "average_odd"
                                )
                            )
                        )

                    with indicator_col2:

                        st.write(
                            "**Variação de mercado:** "
                            + percentage(
                                indicators.get(
                                    "market_variation"
                                )
                            )
                        )

                        st.write(
                            "**Value Bet:** "
                            + (
                                "Sim"
                                if indicators.get(
                                    "is_value_bet",
                                    False,
                                )
                                else "Não"
                            )
                        )

                        st.write(
                            "**Nível de risco:** "
                            + str(
                                indicators.get(
                                    "risk",
                                    "Alto",
                                )
                            )
                        )

                    st.markdown(
                        "### ✅ Pontos favoráveis"
                    )

                    strengths = ai_result.get(
                        "strengths",
                        [],
                    )

                    if strengths:

                        for strength in strengths:

                            st.success(
                                strength
                            )

                    else:

                        st.write(
                            "Nenhum ponto favorável identificado."
                        )

                    st.markdown(
                        "### ⚠️ Pontos de atenção"
                    )

                    warnings = ai_result.get(
                        "warnings",
                        [],
                    )

                    if warnings:

                        for warning in warnings:

                            st.warning(
                                warning
                            )

                    else:

                        st.write(
                            "Nenhum alerta adicional."
                        )

                    st.markdown(
                        "### 🧠 Conclusão da IA"
                    )

                    st.info(
                        ai_result.get(
                            "conclusion",
                            "Sem conclusão disponível.",
                        )
                    )

                    st.caption(
                        "A análise da IA é interpretativa. "
                        "Ela não representa garantia de resultado."
                    )

                else:

                    st.warning(
                        ai_result.get(
                            "message",
                            "A IA não conseguiu gerar uma análise.",
                        )
                    )
