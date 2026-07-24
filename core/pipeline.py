"""
OddReal 2.0
Pipeline Principal
"""

from __future__ import annotations

from typing import Dict

from services.api_client import api_client
from core.analyzer import analyzer
from modules.logger import info


class Pipeline:

    def __init__(self):

        info("Pipeline iniciado.")

    def execute(self) -> Dict:

        events = api_client.get_events()

        analyses = analyzer.analyze(events)

        value_bets = analyzer.value_bets(
            analyses
        )

        best_match = analyzer.best_opportunity(
            analyses
        )

        return {

            "events": events,

            "analyses": analyses,

            "value_bets": value_bets,

            "best_match": best_match,

            "total_events": len(events),

            "total_value_bets": len(value_bets)

        }


pipeline = Pipeline()
