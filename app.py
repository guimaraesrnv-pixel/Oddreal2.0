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
from modules.logger import info, error


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
        background: linear-gradient(
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
    """Formata valores numéricos."""

    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def percentage(value: Any) -> str:
    """Formata percentuais."""

    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def safe_float(value: Any, default: float = 0.0) -> float:
    """Converte um valor para float com segurança."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_result() -> Dict[str, Any]:
    """Retorna o resultado atual do pipeline."""

    result = st.session_state.get("pipeline_result")

    if isinstance(result, dict):
        return result

    return {}


def get_analyses(
    result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Retorna as análises válidas."""

    analyses = result.get("analyses", [])

    if not isinstance(analyses, list):
        return []

    return [
        item
        for item in analyses
        if isinstance(item, dict)
    ]


def get_value_bets(
    result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Retorna as Value Bets."""

    value_bets = result.get("value_bets", [])

    if isinstance(value_bets, list):

        valid = [
            item
            for item in value_bets
            if isinstance(item, dict)
        ]

        if valid:
            return valid

    analyses = get_analyses(result)

    return [
        item
        for item in analyses
        if item.get("is_value_bet") is True
    ]


def event_name(
    item: Dict[str, Any],
) -> str:
    """Monta o nome do evento."""

    name = item.get("event")

    if name:
        return str(name)

    home = item.get(
        "home_team",
        "Mandante",
    )

    away = item.get(
        "away_team",
        "Visitante",
    )

    return f"{home} × {away}"


def market_name(
    item: Dict[str, Any],
) -> str:
    """Retorna o mercado."""

    return str(
        item.get(
            "selected_market",
            item.get(
                "market",
                "Mercado",
            ),
        )
    )


def outcome_name(
    item: Dict[str, Any],
) -> str:
    """Retorna a seleção."""

    return str(
        item.get(
            "selected_outcome",
            item.get(
                "outcome",
                "Seleção",
            ),
        )
    )


def bookmaker_name(
    item: Dict[str, Any],
) -> str:
    """Retorna a casa de apostas."""

    return str(
        item.get(
            "selected_bookmaker",
            item.get(
                "bookmaker",
                "Casa não informada",
            ),
        )
    )


def run_pipeline(
    force_refresh: bool = False,
) -> None:
    """Executa o pipeline principal."""

    try:

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

    except Exception as exc:

        error(
            f"Erro ao executar pipeline: {exc}"
        )

        st.error(
            f"Erro ao atualizar o mercado: {exc}"
        )


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="oddreal-header">
        <h1>⚽ OddReal 2.0</h1>
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
# RESULTADO
# ============================================================

result = get_result()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state["page"] == "Dashboard":

    st.title("Visão geral do mercado")

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
            len(result.get("events", []))
            if isinstance(
                result.get("events"),
                list,
            )
            else 0,
        )

        total_analyses = result.get(
            "total_analyses",
            len(get_analyses(result)),
        )

        total_value_bets = result.get(
            "total_value_bets",
            len(get_value_bets(result)),
        )

        summary = result.get(
            "analysis_summary",
            {},
        )

        if not isinstance(summary, dict):
            summary = {}

        average_index = safe_float(
            summary.get(
                "average_index",
                0,
            )
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Eventos",
                total_events,
            )

        with col2:
            st.metric(
                "Análises",
                total_analyses,
            )

        with col3:
            st.metric(
                "Value Bets",
                total_value_bets,
            )

        with col4:
            st.metric(
                "Índice médio",
                f"{average_index:.2f}",
            )

        st.divider()

        # ========================================================
        # MELHOR OPORTUNIDADE
        # ========================================================

        st.subheader(
            "⭐ Melhor oportunidade"
        )

        best = result.get(
            "best_opportunity"
        )

        if not isinstance(best, dict):

            best = result.get(
                "best_match"
            )

        if isinstance(best, dict):

            st.success(
                "Melhor oportunidade identificada"
            )

            st.markdown(
                f"### {event_name(best)}"
            )

            st.write(
                f"**Mercado:** {market_name(best)}"
            )

            st.write(
                f"**Seleção:** {outcome_name(best)}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Casa",
                    bookmaker_name(best),
                )

            with col2:
                st.metric(
                    "Odd",
                    money_or_number(
                        best.get(
                            "odd",
                            0,
                        )
                    ),
                )

            with col3:
                st.metric(
                    "EV",
                    percentage(
                        best.get(
                            "expected_value",
                            0,
                        )
                    ),
                )

            with col4:
                st.metric(
                    "Índice OddReal",
                    safe_float(
                        best.get(
                            "oddreal_index",
                            0,
                        )
                    ),
                )

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "**Confiança:** "
                    + str(
                        best.get(
                            "confidence_level",
                            "Baixa",
                        )
                    )
                )

            with col2:
                st.write(
                    "**Risco:** "
                    + str(
                        best.get(
                            "risk",
                            "Alto",
                        )
                    )
                )

        else:

            st.info(
                "Nenhuma oportunidade disponível."
            )

        # ========================================================
        # ANÁLISES
        # ========================================================

        st.divider()

        st.subheader(
            "📊 Análises recentes"
        )

        analyses = get_analyses(result)

        if not analyses:

            st.warning(
                "Nenhuma análise foi encontrada."
            )

        else:

            for analysis in analyses[:10]:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {event_name(analysis)}"
                    )

                    st.caption(
                        f"{market_name(analysis)} — "
                        f"{outcome_name(analysis)}"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Odd",
                            money_or_number(
                                analysis.get(
                                    "odd",
                                    0,
                                )
                            ),
                        )

                    with col2:

                        ev_value = safe_float(
                            analysis.get(
                                "expected_value",
                                0,
                            )
                        )

                        st.metric(
                            "EV",
                            percentage(ev_value),
                        )

                    with col3:

                        st.metric(
                            "Índice",
                            safe_float(
                                analysis.get(
                                    "oddreal_index",
                                    0,
                                )
                            ),
                        )

                    with col4:

                        st.metric(
                            "Risco",
                            str(
                                analysis.get(
                                    "risk",
                                    "Alto",
                                )
                            ),
                        )

                    if analysis.get(
                        "is_value_bet",
                        False,
                    ):

                        st.success(
                            "🎯 VALUE BET identificada"
                        )


# ============================================================
# VALUE BETS
# ============================================================

elif st.session_state["page"] == "Value Bets":

    st.title("🎯 Value Bets")

    st.write(
        "Oportunidades identificadas pelo "
        "motor quantitativo do OddReal."
    )

    if not result:

        st.info(
            "Carregue o mercado antes de visualizar "
            "as Value Bets."
        )

        if st.button(
            "🚀 Carregar mercado",
            type="primary",
            use_container_width=True,
        ):

            run_pipeline()
            st.rerun()

    else:

        value_bets = get_value_bets(result)

        if not value_bets:

            st.warning(
                "Nenhuma Value Bet foi encontrada "
                "no mercado atual."
            )

        else:

            st.success(
                f"{len(value_bets)} "
                "oportunidade(s) encontrada(s)."
            )

            for opportunity in value_bets:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🎯 {event_name(opportunity)}"
                    )

                    st.caption(
                        f"{market_name(opportunity)} — "
                        f"{outcome_name(opportunity)}"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Casa",
                            bookmaker_name(
                                opportunity
                            ),
                        )

                    with col2:

                        st.metric(
                            "Odd",
                            money_or_number(
                                opportunity.get(
                                    "odd",
                                    0,
                                )
                            ),
                        )

                    with col3:

                        st.metric(
                            "Probabilidade",
                            percentage(
                                opportunity.get(
                                    "probability",
                                    0,
                                )
                            ),
                        )

                    with col4:

                        st.metric(
                            "EV",
                            percentage(
                                opportunity.get(
                                    "expected_value",
                                    0,
                                )
                            ),
                        )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.write(
                            "**Índice OddReal:** "
                            + str(
                                opportunity.get(
                                    "oddreal_index",
                                    0,
                                )
                            )
                        )

                    with col2:

                        st.write(
                            "**Risco:** "
                            + str(
                                opportunity.get(
                                    "risk",
                                    "Alto",
                                )
                            )
                        )

                    with col3:

                        st.write(
                            "**Confiança:** "
                            + str(
                                opportunity.get(
                                    "confidence_level",
                                    "Baixa",
                                )
                            )
                        )

                    with col4:

                        st.write(
                            "**Odd média:** "
                            + money_or_number(
                                opportunity.get(
                                    "average_odd",
                                    0,
                                )
                            )
                        )

                    variation = opportunity.get(
                        "market_variation",
                        0,
                    )

                    st.write(
                        "**Variação de mercado:** "
                        + percentage(variation)
                    )


# ============================================================
# INTELIGÊNCIA ARTIFICIAL
# ============================================================

elif st.session_state["page"] == "IA":

    st.title(
        "🤖 Inteligência Artificial"
    )

    st.write(
        """
        A inteligência do OddReal interpreta os
        indicadores matemáticos produzidos pelo
        motor quantitativo.

        A IA não altera odds, probabilidades ou EV.
        Ela atua como uma camada interpretativa
        sobre os dados calculados pelo sistema.
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

        analyses = get_analyses(result)

        if not analyses:

            st.warning(
                "Não existem análises disponíveis "
                "para a inteligência artificial."
            )

        else:

            options = []

            for index, item in enumerate(
                analyses
            ):

                options.append(
                    f"{index + 1}. "
                    f"{event_name(item)}"
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

            st.subheader(
                "🎯 Evento selecionado"
            )

            st.info(
                f"{event_name(selected_analysis)} — "
                f"{market_name(selected_analysis)} — "
                f"{outcome_name(selected_analysis)}"
            )

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

                        error(
                            f"Erro na análise IA: {exc}"
                        )

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

                    st.divider()

                    st.subheader(
                        "📊 Diagnóstico técnico"
                    )

                    col1, col2, col3, col4 = st.columns(4)

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
                            safe_float(
                                indicators.get(
                                    "oddreal_index",
                                    selected_analysis.get(
                                        "oddreal_index",
                                        0,
                                    ),
                                )
                            ),
                        )

                    with col4:

                        st.metric(
                            "Risco",
                            str(
                                indicators.get(
                                    "risk",
                                    selected_analysis.get(
                                        "risk",
                                        "Alto",
                                    ),
                                )
                            ),
                        )

                    st.subheader(
                        "📊 Indicadores completos"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

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

                    with col2:

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

                    st.subheader(
                        "✅ Pontos favoráveis"
                    )

                    strengths = ai_result.get(
                        "strengths",
                        [],
                    )

                    if isinstance(
                        strengths,
                        list,
                    ) and strengths:

                        for strength in strengths:

                            st.success(
                                str(strength)
                            )

                    else:

                        st.write(
                            "Nenhum ponto favorável "
                            "identificado."
                        )

                    st.subheader(
                        "⚠️ Pontos de atenção"
                    )

                    warnings = ai_result.get(
                        "warnings",
                        [],
                    )

                    if isinstance(
                        warnings,
                        list,
                    ) and warnings:

                        for warning in warnings:

                            st.warning(
                                str(warning)
                            )

                    else:

                        st.write(
                            "Nenhum alerta adicional."
                        )

                    st.subheader(
                        "🧠 Conclusão da IA"
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
# FALLBACK
# ============================================================

else:

    st.session_state["page"] = "Dashboard"
    st.rerun()
