"""
OddReal 2.0
Página de Value Bets
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


def _number(
    value: Any,
    default: float = 0.0,
) -> float:
    """Converte um valor para número com segurança."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _percent(
    value: Any,
) -> str:
    """Formata um número como percentual."""

    return f"{_number(value):.2f}%"


def _odd(
    value: Any,
) -> str:
    """Formata uma odd."""

    number = _number(value)

    if number <= 0:
        return "-"

    return f"{number:.2f}"


def _match_name(
    opportunity: Dict[str, Any],
) -> str:
    """Obtém o nome da partida."""

    home = (
        opportunity.get("home_team")
        or opportunity.get("home")
        or "Mandante"
    )

    away = (
        opportunity.get("away_team")
        or opportunity.get("away")
        or "Visitante"
    )

    return f"{home} x {away}"


def _sort_opportunities(
    opportunities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Ordena as oportunidades pelo Índice OddReal.
    """

    return sorted(
        opportunities,
        key=lambda item: _number(
            item.get(
                "oddreal_index",
                0,
            )
        ),
        reverse=True,
    )


def _render_summary(
    opportunities: List[Dict[str, Any]],
) -> None:

    total = len(opportunities)

    ev_values = [
        _number(
            item.get(
                "expected_value",
                0,
            )
        )
        for item in opportunities
    ]

    index_values = [
        _number(
            item.get(
                "oddreal_index",
                0,
            )
        )
        for item in opportunities
    ]

    average_ev = (
        sum(ev_values) / len(ev_values)
        if ev_values
        else 0
    )

    best_index = (
        max(index_values)
        if index_values
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💎 Oportunidades",
            total,
        )

    with col2:
        st.metric(
            "📈 EV médio",
            _percent(average_ev),
        )

    with col3:
        st.metric(
            "🎯 Melhor Índice",
            f"{best_index:.0f}",
        )

    with col4:

        low_risk = sum(
            1
            for item in opportunities
            if str(
                item.get(
                    "risk",
                    "",
                )
            ).lower()
            == "baixo"
        )

        st.metric(
            "🛡️ Baixo risco",
            low_risk,
        )


def _render_opportunity(
    opportunity: Dict[str, Any],
    position: int,
) -> None:

    match = _match_name(
        opportunity
    )

    odd = opportunity.get(
        "odd",
        opportunity.get(
            "best_odd",
            0,
        ),
    )

    ev = opportunity.get(
        "expected_value",
        0,
    )

    probability = opportunity.get(
        "probability",
        0,
    )

    index = opportunity.get(
        "oddreal_index",
        0,
    )

    confidence = opportunity.get(
        "confidence_level",
        "Não calculada",
    )

    risk = opportunity.get(
        "risk",
        "Não calculado",
    )

    average_odd = opportunity.get(
        "average_odd",
        0,
    )

    variation = opportunity.get(
        "market_variation",
        0,
    )

    with st.container(border=True):

        st.markdown(
            f"### #{position} — {match}"
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Odd",
                _odd(odd),
            )

        with col2:
            st.metric(
                "EV",
                _percent(ev),
            )

        with col3:
            st.metric(
                "Probabilidade",
                _percent(probability),
            )

        with col4:
            st.metric(
                "Índice OddReal",
                index,
            )

        with col5:
            st.metric(
                "Risco",
                risk,
            )

        st.divider()

        detail1, detail2, detail3 = st.columns(3)

        with detail1:

            st.markdown(
                f"**Confiança:** {confidence}"
            )

        with detail2:

            st.markdown(
                f"**Odd média:** {_odd(average_odd)}"
            )

        with detail3:

            st.markdown(
                "**Variação do mercado:** "
                f"{_percent(variation)}"
            )

        if _number(ev) > 10:

            st.success(
                "🔥 EV elevado em relação "
                "aos critérios atuais."
            )

        elif _number(ev) > 5:

            st.info(
                "💎 Valor esperado positivo "
                "identificado."
            )

        else:

            st.warning(
                "⚠️ Oportunidade próxima do "
                "limite de classificação."
            )


def render(
    opportunities: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> None:
    """
    Renderiza a página de Value Bets.

    As oportunidades devem vir do Pipeline.
    """

    st.title(
        "💎 Value Bets"
    )

    st.caption(
        "Oportunidades identificadas pelo "
        "motor quantitativo do OddReal."
    )

    if not opportunities:

        st.warning(
            "Nenhuma Value Bet encontrada "
            "com os dados disponíveis."
        )

        st.info(
            "As oportunidades aparecem aqui "
            "quando o motor identifica valor "
            "esperado positivo de acordo com "
            "os critérios configurados."
        )

        return

    valid_opportunities = [

        item

        for item in opportunities

        if isinstance(
            item,
            dict,
        )

    ]

    if not valid_opportunities:

        st.warning(
            "Os dados recebidos não possuem "
            "formato válido para análise."
        )

        return

    opportunities = _sort_opportunities(
        valid_opportunities
    )

    _render_summary(
        opportunities
    )

    st.divider()

    st.subheader(
        "🔥 Melhores oportunidades"
    )

    for position, opportunity in enumerate(
        opportunities,
        start=1,
    ):

        _render_opportunity(
            opportunity,
            position,
    )
