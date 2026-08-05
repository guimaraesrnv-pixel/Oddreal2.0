"""
OddReal 2.0
Central de Análise de Odds

Fluxo:

The Odds API
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
    st.session_state["pipeline_result"] = None

if "ai_result" not in st.session_state:
    st.session_state["ai_result"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

if "selected_analysis" not in st.session_state:
    st.session_state["selected_analysis"] = None


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def money_or_number(value: Any) -> str:
    """
    Formata valores numéricos.
    """

    if value is None:
        return "0.00"

    try:
        return f"{float(value):.2f}"

    except (TypeError, ValueError):
        return "0.00"


def percentage(value: Any) -> str:
    """
    Formata valores percentuais.
    """

    if value is None:
        return "0.00%"

    try:
        return f"{float(value):.2f}%"

    except (TypeError, ValueError):
        return "0.00%"


def get_result() -> Dict[str, Any]:
    """
    Recupera o resultado atual do pipeline.
    """

    result = st.session_state.get(
        "pipeline_result"
    )

    if not isinstance(result, dict):
        return {}

    return result


def run_pipeline(
    force_refresh: bool = False,
) -> None:
    """
    Executa o pipeline principal.
    """

    with st.spinner(
        "Atualizando eventos e analisando o mercado..."
    ):
        result = pipeline.execute(
            force_refresh=force_refresh
        )

    if not isinstance(result, dict):
        result = {}

    st.session_state["pipeline_result"] = result
    st.session_state["ai_result"] = None

    info("Dashboard atualizado.")


def get_analyses(
    result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Recupera análises válidas.
    """

    analyses = result.get(
        "analyses",
        [],
    )

    if not isinstance(
        analyses,
        list,
    ):
        return []

    return [
        item
        for item in analyses
        if isinstance(item, dict)
    ]


def get_value_bets(
    result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Recupera Value Bets válidas.
    """

    value_bets = result.get(
        "value_bets",
        [],
    )

    if not isinstance(
        value_bets,
        list,
    ):
        return []

    return [
        item
        for item in value_bets
        if isinstance(item, dict)
    ]


def event_name_from_data(
    item: Dict[str, Any],
) -> str:
    """
    Monta o nome do evento de forma compatível
    com diferentes estruturas de dados.
    """

    event_name = item.get(
        "event",
        "",
    )

    if event_name:
        return str(event_name)

    home_team = item.get(
        "home_team",
        "Mandante",
    )

    away_team = item.get(
        "away_team",
        "Visitante",
    )

    return (
        f"{home_team} × {away_team}"
    )


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Conversão numérica segura.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


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

nav1, nav2, nav3, nav4 = st.columns(4)


with nav1:

    if st.button(
        "📊 Dashboard",
        use_container_width=True,
    ):
        st.session_state["page"] = "Dashboard"
        st.session_state["ai_result"] = None
        st.rerun()


with nav2:

    if st.button(
        "🎯 Value Bets",
        use_container_width=True,
    ):
        st.session_state["page"] = "Value Bets"
        st.rerun()


with nav3:

    if st.button(
        "🤖 Inteligência IA",
        use_container_width=True,
    ):
        st.session_state["page"] = "IA"
        st.rerun()


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

if st.session_state["page"] == "Dashboard":

    st.markdown(
        '<div class="section-title">'
        "Visão geral do mercado"
        "</div>",
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

        if not isinstance(
            summary,
            dict,
        ):
            summary = {}

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


        # ========================================================
        # MELHOR OPORTUNIDADE
        # ========================================================

        st.markdown(
            '<div class="section-title">'
            "⭐ Melhor oportunidade"
            "</div>",
            unsafe_allow_html=True,
        )

        best_opportunity = result.get(
            "best_opportunity"
        )

        if not best_opportunity:
            best_opportunity = result.get(
                "best_match"
            )

        if isinstance(
            best_opportunity,
            dict,
        ) and best_opportunity:

            event_name = event_name_from_data(
                best_opportunity
            )

            market_name = best_opportunity.get(
                "selected_market",
                best_opportunity.get(
                    "market",
                    "Mercado",
                ),
            )

            outcome_name = best_opportunity.get(
                "selected_outcome",
                best_opportunity.get(
                    "outcome",
                    "Seleção",
                ),
            )

            odd = best_opportunity.get(
                "odd",
                0,
            )

            ev = best_opportunity.get(
                "expected_value",
                0,
            )

            index = best_opportunity.get(
                "oddreal_index",
                0,
            )

            confidence = best_opportunity.get(
                "confidence_level",
                "Não informado",
            )

            risk = best_opportunity.get(
                "risk",
                "Alto",
            )

            bookmaker = best_opportunity.get(
                "selected_bookmaker",
                best_opportunity.get(
                    "bookmaker",
                    "Casa não informada",
                ),
            )

            st.markdown(
                f"""
                <div class="analysis-card">

                    <span class="badge">
                        ⭐ MELHOR OPORTUNIDADE
                    </span>

                    <h3>
                        {event_name}
                    </h3>

                    <p class="muted">
                        {market_name} —
                        {outcome_name}
                    </p>

                    <hr>

                    <b>Casa:</b>
                    {bookmaker}

                    &nbsp;&nbsp;

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


        # ========================================================
        # ANÁLISES RECENTES
        # ========================================================

        st.markdown(
            '<div class="section-title">'
            "📊 Análises recentes"
            "</div>",
            unsafe_allow_html=True,
        )

        analyses = get_analyses(
            result
        )

        if not analyses:

            st.warning(
                "Nenhuma análise foi encontrada."
            )

        else:

            for analysis in analyses[:10]:

                event_name = event_name_from_data(
                    analysis
                )

                market_name = analysis.get(
                    "selected_market",
                    analysis.get(
                        "market",
                        "Mercado",
                    ),
                )

                outcome_name = analysis.get(
                    "selected_outcome",
                    "Seleção",
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

                confidence = analysis.get(
                    "confidence_level",
                    "Não informado",
                )

                risk = analysis.get(
                    "risk",
                    "Alto",
                )

                is_value = bool(
                    analysis.get(
                        "is_value_bet",
                        False,
                    )
                )

                ev_class = (
                    "positive"
                    if safe_float(ev) >= 0
                    else "negative"
                )

                value_label = (
                    "🎯 VALUE BET"
                    if is_value
                    else "Análise"
                )

                st.markdown(
                    f"""
                    <div class="analysis-card">

                        <span class="badge">
                            {value_label}
                        </span>

                        <h4>
                            {event_name}
                        </h4>

                        <p class="muted">
                            {market_name} —
                            {outcome_name}
                        </p>

                        <p>
                            <b>Odd:</b>
                            {money_or_number(odd)}

                            &nbsp;&nbsp;

                            <b>EV:</b>

                            <span class="{ev_class}">
                                {percentage(ev)}
                            </span>

                            &nbsp;&nbsp;

                            <b>Índice:</b>
                            {index}
                        </p>

                        <p>
                            <b>Confiança:</b>
                            {confidence}

                            &nbsp;&nbsp;

                            <b>Risco:</b>
                            {risk}
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# VALUE BETS
# ============================================================

elif st.session_state["page"] == "Value Bets":

    st.markdown(
        '<div class="section-title">'
        "🎯 Value Bets"
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        """
        Aqui são exibidas as oportunidades identificadas
        pelo motor quantitativo do OddReal com base em
        valor esperado, probabilidade, índice OddReal
        e condições do mercado.
        """
    )

    if not result:

        st.info(
            "Carregue o mercado antes de visualizar as Value Bets."
        )

        if st.button(
            "🚀 Carregar mercado",
            type="primary",
            use_container_width=True,
        ):
            run_pipeline()
            st.rerun()

    else:

        value_bets = get_value_bets(
            result
        )

        # Fallback para análises que possuem
        # is_value_bet=True.
        if not value_bets:

            analyses = get_analyses(
                result
            )

            value_bets = [
                analysis
                for analysis in analyses
                if bool(
                    analysis.get(
                        "is_value_bet",
                        False,
                    )
                )
            ]

        if not value_bets:

            st.warning(
                "Nenhuma Value Bet foi encontrada "
                "com os critérios atuais."
            )

        else:

            st.success(
                f"{len(value_bets)} "
                "oportunidade(s) encontrada(s)."
            )

            for opportunity in value_bets:

                event_name = event_name_from_data(
                    opportunity
                )

                market_name = opportunity.get(
                    "selected_market",
                    opportunity.get(
                        "market",
                        "Mercado",
                    ),
                )

                outcome_name = opportunity.get(
                    "selected_outcome",
                    opportunity.get(
                        "outcome",
                        "Resultado",
                    ),
                )

                bookmaker = opportunity.get(
                    "selected_bookmaker",
                    opportunity.get(
                        "bookmaker",
                        "Casa não informada",
                    ),
                )

                odd = opportunity.get(
                    "odd",
                    0,
                )

                probability = opportunity.get(
                    "probability",
                    opportunity.get(
                        "confidence",
                        0,
                    ),
                )

                ev = opportunity.get(
                    "expected_value",
                    0,
                )

                index = opportunity.get(
                    "oddreal_index",
                    0,
                )

                risk = opportunity.get(
                    "risk",
                    "Alto",
                )

                confidence = opportunity.get(
                    "confidence_level",
                    "Baixa",
                )

                average_odd = opportunity.get(
                    "average_odd",
                    0,
                )

                variation = opportunity.get(
                    "market_variation",
                    0,
                )

                st.markdown(
                    f"""
                    <div class="analysis-card">

                        <span class="badge">
                            🎯 VALUE BET
                        </span>

                        <h3>
                            {event_name}
                        </h3>

                        <p class="muted">
                            {market_name} —
                            {outcome_name}
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

                        <b>Risco:</b>
                        {risk}

                        &nbsp;&nbsp;

                        <b>Confiança:</b>
                        {confidence}

                        <br><br>

                        <b>Odd média do mercado:</b>
                        {money_or_number(average_odd)}

                        &nbsp;&nbsp;

                        <b>Variação:</b>
                        {percentage(variation)}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# INTELIGÊNCIA ARTIFICIAL
# ============================================================

elif st.session_state["page"] == "IA":

    st.markdown(
        '<div class="section-title">'
        "🤖 Inteligência Artificial"
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        """
        A inteligência do OddReal interpreta os indicadores
        matemáticos produzidos pelo motor quantitativo.

        A IA não altera odds, probabilidades ou EV.
        Ela atua como uma camada interpretativa sobre
        os dados calculados pelo sistema.
        """
    )

    if not result:

        st.info(
            "Carregue o mercado antes de utilizar a IA."
        )

        if st.button(
            "🚀 Carregar mercado",
            type="primary",
            use_container_width=True,
        ):
            run_pipeline()
            st.rerun()

    else:

        analyses = get_analyses(
            result
        )

        if not analyses:

            st.warning(
                "Não existem análises disponíveis "
                "para a inteligência artificial."
            )

        else:

            # ====================================================
            # SELEÇÃO DO EVENTO
            # ====================================================

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

            st.session_state[
                "selected_analysis"
            ] = selected_analysis

            # ====================================================
            # EVENTO SELECIONADO
            # ====================================================

            st.markdown(
                "### 🎯 Evento selecionado"
            )

            selected_home = selected_analysis.get(
                "home_team",
                "Mandante",
            )

            selected_away = selected_analysis.get(
                "away_team",
                "Visitante",
            )

            selected_market = selected_analysis.get(
                "selected_market",
                selected_analysis.get(
                    "market",
                    "Mercado",
                ),
            )

            selected_outcome = selected_analysis.get(
                "selected_outcome",
                "Seleção",
            )

            st.info(
                f"{selected_home} × "
                f"{selected_away} — "
                f"{selected_market} — "
                f"{selected_outcome}"
            )

            # ====================================================
            # BOTÃO DA IA
            # ====================================================

            if st.button(
                "🤖 Analisar com IA",
                type="primary",
                use_container_width=True,
            ):

                with st.spinner(
                    "A IA está interpretando os indicadores..."
                ):

                    try:

                        ai_result = ai_engine.analyze(
                            selected_analysis
                        )

                    except Exception as exc:

                        ai_result = {
                            "status": "error",
                            "message": (
                                "Erro ao executar "
                                f"a análise da IA: {exc}"
                            ),
                        }

                st.session_state[
                    "ai_result"
                ] = ai_result

                st.rerun()

            # ====================================================
            # RESULTADO DA IA
            # ====================================================

            ai_result = st.session_state.get(
                "ai_result"
            )

            if ai_result:

                if not isinstance(
                    ai_result,
                    dict,
                ):

                    st.error(
                        "A IA retornou um formato "
                        "de resposta inválido."
                    )

                elif ai_result.get(
                    "status"
                ) == "success":

                    indicators = ai_result.get(
                        "indicators",
                        {},
                    )

                    if not isinstance(
                        indicators,
                        dict,
                    ):
                        indicators = {}

                    # ==========================================
                    # DIAGNÓSTICO TÉCNICO
                    # ==========================================

                    st.markdown(
                        '<div class="section-title">'
                        "📊 Diagnóstico técnico"
                        "</div>",
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
                                    "odd",
                                    selected_analysis.get(
                                        "odd",
                                        0,
                                    ),
                                )
                            ),
                        )

                    with col2:

                        st.metric(
                            "EV",
                            percentage(
                                indicators.get(
                                    "expected_value",
                                    selected_analysis.get(
                                        "expected_value",
                                        0,
                                    ),
                                )
                            ),
                        )

                    with col3:

                        st.metric(
                            "Índice OddReal",
                            indicators.get(
                                "oddreal_index",
                                selected_analysis.get(
                                    "oddreal_index",
                                    0,
                                ),
                            ),
                        )

                    with col4:

                        st.metric(
                            "Risco",
                            indicators.get(
                                "risk",
                                selected_analysis.get(
                                    "risk",
                                    "Alto",
                                ),
                            ),
                        )

                    # ==========================================
                    # INDICADORES COMPLETOS
                    # ==========================================

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
                                    "probability",
                                    selected_analysis.get(
                                        "probability",
                                        0,
                                    ),
                                )
                            )
                        )

                        st.write(
                            "**Confiança:** "
                            + str(
                                indicators.get(
                                    "confidence_level",
                                    selected_analysis.get(
                                        "confidence_level",
                                        "Não informado",
                                    ),
                                )
                            )
                        )

                        st.write(
                            "**Odd média do mercado:** "
                            + money_or_number(
                                indicators.get(
                                    "average_odd",
                                    selected_analysis.get(
                                        "average_odd",
                                        0,
                                    ),
                                )
                            )
                        )

                    with indicator_col2:

                        st.write(
                            "**Variação de mercado:** "
                            + percentage(
                                indicators.get(
                                    "market_variation",
                                    selected_analysis.get(
                                        "market_variation",
                                        0,
                                    ),
                                )
                            )
                        )

                        is_value_bet = indicators.get(
                            "is_value_bet",
                            selected_analysis.get(
                                "is_value_bet",
                                False,
                            ),
                        )

                        st.write(
                            "**Value Bet:** "
                            + (
                                "Sim"
                                if is_value_bet
                                else "Não"
                            )
                        )

                        st.write(
                            "**Nível de risco:** "
                            + str(
                                indicators.get(
                                    "risk",
                                    selected_analysis.get(
                                        "risk",
                                        "Alto",
                                    ),
                                )
                            )
                        )

                    # ==========================================
                    # PONTOS FAVORÁVEIS
                    # ==========================================

                    st.markdown(
                        "### ✅ Pontos favoráveis"
                    )

                    strengths = ai_result.get(
                        "strengths",
                        [],
                    )

                    if not isinstance(
                        strengths,
                        list,
                    ):
                        strengths = []

                    if strengths:

                        for strength in strengths:
                            st.success(
                                str(strength)
                            )

                    else:

                        st.write(
                            "Nenhum ponto favorável "
                            "identificado."
                        )

                    # ==========================================
                    # PONTOS DE ATENÇÃO
                    # ==========================================

                    st.markdown(
                        "### ⚠️ Pontos de atenção"
                    )

                    warnings = ai_result.get(
                        "warnings",
                        [],
                    )

                    if not isinstance(
                        warnings,
                        list,
                    ):
                        warnings = []

                    if warnings:

                        for warning in warnings:
                            st.warning(
                                str(warning)
                            )

                    else:

                        st.write(
                            "Nenhum alerta adicional."
                        )

                    # ==========================================
                    # CONCLUSÃO
                    # ==========================================

                    st.markdown(
                        "### 🧠 Conclusão da IA"
                    )

                    conclusion = ai_result.get(
                        "conclusion",
                        "Sem conclusão disponível.",
                    )

                    if conclusion is None:
                        conclusion = (
                            "Sem conclusão disponível."
                        )

                    st.info(
                        str(conclusion)
                    )

                    # ==========================================
                    # AVISO
                    # ==========================================

                    st.caption(
                        "A análise da IA é interpretativa. "
                        "Ela não representa garantia de resultado "
                        "e não substitui uma avaliação própria."
                    )

                else:

                    st.warning(
                        ai_result.get(
                            "message",
                            "A IA não conseguiu "
                            "gerar uma análise.",
                        )
                    )


# ============================================================
# PÁGINA DESCONHECIDA
# ============================================================

else:

    st.session_state["page"] = "Dashboard"
    st.rerun()
          
