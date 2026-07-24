"""
OddReal 2.0
Analisador Principal
"""

from oddsengine.odds import OddsEngine


class Analyzer:

    def __init__(self):

        self.engine = OddsEngine()

    def analyze(self, events):

        analyses = []

        for event in events:

            result = self.engine.analyze_event(event)

            analyses.append(result)

        return analyses


analyzer = Analyzer()
