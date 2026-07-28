"""
OddReal 2.0
Dashboard Principal
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


def _format_percent(value: Any) -> str:
    """Formata um valor percentual com segurança."""

    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def _format_odd(value: Any) -> str:
    """Formata uma odd com segurança."""

    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "-"


def _event_name(event: Dict[str, Any]) -> str:
    """Obtém o nome da partida."""

    home = (
        event.get("home_team")
        or event.get("home")
        or "Mandante"
    )

    away = (
        event.get("away_team")
        or event.get("away")
        or "Visitante"
    )

    return f"{home} x {away}"


def _render_metric_cards(
    total_events: int,
    total_valuebets: int,
    best_ev: Any,
    average_confidence: Any,
) -> None:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚽ Eventos",
            total_events,
        )

    with col2:
        st.metric(
            "💎 Value Bets",
            total_valuebets,
        )

    with col3:
        st.metric(
            "🎯 Confiança Média",
            _format_percent(average_confidence),
        )

    with col4:
        st.metric(
            "🔥 Melhor EV",
            _format_percent(best_ev),
        )


def _render_best_opportunity(
    best_match: Optional[Dict[str, Any]],
) -> None:

    st.subheader("🔥 Melhor oportunidade do momento")

    if not best_match:
        st.info(
            "Nenhuma oportunidade foi identificada "
            "com os dados disponíveis."
        )
        return

    with st.container(border=True):

        st.markdown(
            f"### {_event_name(best_match)}"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Índice OddReal",
                best_match.get(
                    "oddreal_index",
                    0,
                ),
            )

        with col2:
            st.metric(
                "EV",
                _format_percent(
                    best_match.get(
                        "expected_value",
                        0,
                    )
                ),
            )

        with col3:
            st.metric(
                "Odd",
                _format_odd(
                    best_match.get(
                        "odd",
                        best_match.get(
                            "best_odd",
                            0,
                        ),
                    )
                ),
            )

        with col4:
            st.metric(
                "Risco",
                best_match.get(
                    "risk",
                    "Não calculado",
                ),
            )


def _render_value_bets(
    value_bets: List[Dict[str, Any]],
) -> None:

    st.subheader("💎 Value Bets em destaque")

    if not value_bets:
        st.info(
            "Nenhuma Value Bet disponível no momento."
        )
        return

    for opportunity in value_bets[:5]:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [4, 1, 1]
            )

            with col1:

                st.markdown(
                    f"**{_event_name(opportunity)}**"
                )

                st.caption(
                    "Oportunidade identificada "
                    "pelo motor de análise."
                )

            with col2:

                st.metric(
                    "EV",
                    _format_percent(
                        opportunity.get(
                            "expected_value",
                            0,
                        )
                    ),
                )

            with col3:

                st.metric(
                    "Índice",
                    opportunity.get(
                        "oddreal_index",
                        0,
                    ),
                )


def _render_recent_events(
    events: List[Dict[str, Any]],
) -> None:

    st.subheader("📋 Eventos analisados")

    if not events:

        st.info(
            "Nenhum evento disponível."
        )

        return

    rows = []

    for event in events[:10]:

        rows.append(
            {
                "Partida": _event_name(event),
                "Esporte": event.get(
                    "sport_title",
                    event.get(
                        "sport_key",
                        "-",
                    ),
                ),
                "Início": event.get(
                    "commence_time",
                    "-",
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


def render(
    data: Optional[Dict[str, Any]] = None,
) -> None:

    data = data or {}

    events = data.get(
        "events",
        [],
    )

    analyses = data.get(
        "analyses",
        [],
    )

    value_bets = data.get(
        "value_bets",
        [],
    )

    best_match = data.get(
        "best_match",
    )

    total_events = len(events)

    total_valuebets = len(
        value_bets
    )

    confidence_values = [

        float(
            item.get(
                "probability",
                0,
            )
        )

        for item in analyses

        if isinstance(item, dict)

    ]

    if confidence_values:

        average_confidence = (
            sum(confidence_values)
            / len(confidence_values)
        )

    else:

        average_confidence = 0

    ev_values = [

        float(
            item.get(
                "expected_value",
                0,
            )
        )

        for item in analyses

        if isinstance(item, dict)

    ]

    best_ev = (
        max(ev_values)
        if ev_values
        else 0
    )

    st.title(
        "⚽ OddReal 2.0"
    )

    st.caption(
        "Central inteligente de análise "
        "de odds e oportunidades."
    )

    _render_metric_cards(
        total_events=total_events,
        total_valuebets=total_valuebets,
        best_ev=best_ev,
        average_confidence=average_confidence,
    )

    st.divider()

    _render_best_opportunity(
        best_match
    )

    st.divider()

    _render_value_bets(
        value_bets
    )

    st.divider()

    _render_recent_events(
        events
    )
