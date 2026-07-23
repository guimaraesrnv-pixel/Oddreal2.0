"""
OddReal 2.0

Aplicação principal.
"""

import streamlit as st

from config.config import Config

from services.api import OddsAPI

from core.analyzer import Analyzer

from app.dashboard import dashboard

from database.storage import Storage


storage = Storage()

api = OddsAPI()

analyzer = Analyzer()


def load_data():
    """
    Carrega dados da API.
    """

    try:

        events = api.get_events()

        return events

    except Exception as error:

        st.error(f"Erro: {error}")

        return []
        def process(events):
    """
    Processa análises.
    """

    analyses = []

    for event in events:

        result = analyzer.analyze(event)

        analyses.append(result)

        storage.save(result)

    return analyses
    def main():

    dashboard.configure_page()

    events = load_data()

    results = process(events)

    dashboard.render({

        "events": len(events),

        "results": results

    })


if __name__ == "__main__":

    main()
