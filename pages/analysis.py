"""
OddReal 2.0
Página de Análises
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


def _number(
    value: Any,
    decimals: int = 2,
) -> float:

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _percent(
    value: Any,
) -> str:

    return f"{_number(value):.2f}%"


def _odd(
    value: Any,
) -> str:

    number = _number(value)

    if number <= 0:
        return "-"

    return f"{number:.2f}"


def _match_name(
    result: Dict[str, Any],
) -> str:

    home = (
        result.get("home_team")
        or result.get("home")
        or "Mandante"
    )

    away = (
        result.get("away_team")
        or result.get("away")
        or "Visitante"
    )

    return f"{home} x {away}"


def _render_summary(
    results: List[Dict[str, Any]],
) -> None:

    total = len(results)

    value_bets = sum(
        1
        for result in results
        if result.get(
            "is_value_bet",
            False,
        )
    )

    indexes = [
        _number(
            result.get(
                "oddreal_index",
                0,
            )
        )
        for result in results
    ]

    average_index = (
        sum(indexes) / len(indexes)
        if indexes
        else 0
    )

    ev_values = [
        _number(
            result.get(
                "expected_value",
                0,
            )
        )
        for result in results
    ]

    best_ev = (
        max(ev_values)
        if ev_values
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚽ Jogos analisados",
            total,
        )

    with col2:
        st.metric(
            "💎 Value Bets",
            value_bets,
        )

    with col3:
        st.metric(
            "🎯 Índice médio",
            f"{average_index:.0f}",
        )

    with col4:
        st.metric(
            "📈 Melhor EV",
            _percent(best_ev),
        )


def _render_result(
    result: Dict[str, Any],
    index: int,
) -> None:

    match = _match_name(result)

    odd = result.get(
        "odd",
        result.get(
            "best_odd",
            0,
        ),
    )

    probability = result.get(
        "probability",
        0,
    )

    ev = result.get(
        "expected_value",
        0,
    )

    oddreal_index = result.get(
        "oddreal_index",
        0,
    )

    confidence = result.get(
        "confidence_level",
        "Não calculada",
    )

    risk = result.get(
        "risk",
        "Não calculado",
    )

    is_value_bet = result.get(
        "is_value_bet",
        False,
    )

    with st.expander(
        f"{index + 1}. {match}",
        expanded=index == 0,
    ):

        if is_value_bet:

            st.success(
                "💎 Value Bet identificada"
            )

        else:

            st.info(
                "Sem Value Bet identificada "
                "pelos critérios atuais."
            )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Odd",
                _odd(odd),
            )

        with col2:
            st.metric(
                "Probabilidade",
                _percent(probability),
            )

        with col3:
            st.metric(
                "EV",
                _percent(ev),
            )

        with col4:
            st.metric(
                "Índice OddReal",
                oddreal_index,
            )

        with col5:
            st.metric(
                "Risco",
                risk,
            )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"**Confiança:** {confidence}"
            )

            average_odd = result.get(
                "average_odd",
                0,
            )

            st.markdown(
                f"**Odd média do mercado:** "
                f"{_odd(average_odd)}"
            )

        with col2:

            variation = result.get(
                "market_variation",
                0,
            )

            st.markdown(
                f"**Variação em relação ao "
                f"mercado:** {_percent(variation)}"
            )

            sport = result.get(
                "sport_title",
                result.get(
                    "sport_key",
                    "Não informado",
                ),
            )

            st.markdown(
                f"**Esporte:** {sport}"
            )


def render(
    results: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> None:

    st.title(
        "📊 Análise de Jogos"
    )

    st.caption(
        "Análise quantitativa das oportunidades "
        "processadas pelo OddReal."
    )

    if not results:

        st.info(
            "Nenhuma análise disponível "
            "no momento."
        )

        return

    _render_summary(
        results
    )

    st.divider()

    st.subheader(
        "🔎 Resultados detalhados"
    )

    for index, result in enumerate(
        results
    ):

        if not isinstance(
            result,
            dict,
        ):
            continue

        _render_result(
            result,
            index,
    )
