"""
OddReal 2.0
Pipeline Principal
"""

from services.api_client import OddsAPIClient
from core.analyzer import Analyzer


class Pipeline:

    def __init__(self):

        self.api = OddsAPIClient()
        self.analyzer = Analyzer()

    def run(self):

        events = self.api.get_events()

        if not events:
            return {
                "events": [],
                "analysis": [],
                "value_bets": []
            }

        analysis = self.analyzer.analyze(events)

        return {

            "events": events,

            "analysis": analysis,

            "value_bets": [
                item
                for item in analysis
                if item.get("is_value_bet", False)
            ]

        }


pipeline = Pipeline()
