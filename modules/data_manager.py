"""
OddReal 2.0
Gerenciador de Dados

Responsável por:

- Receber dados da API;
- Validar eventos;
- Limpar estruturas inválidas;
- Padronizar informações;
- Preservar dados brutos;
- Preparar dados para análise;
- Preparar dados para histórico;
- Preparar dados para a IA;
- Fornecer estatísticas básicas do conjunto coletado.

Este módulo NÃO calcula odds nem Value Bets.
Essas responsabilidades permanecem no OddsEngine.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from modules.logger import info, error


class DataManager:
    """
    Camada responsável pelo ciclo de vida dos dados.
    """

    def __init__(self) -> None:

        self.last_raw_events: List[
            Dict[str, Any]
        ] = []

        self.last_clean_events: List[
            Dict[str, Any]
        ] = []

        self.last_processed_at: Optional[
            str
        ] = None

        info(
            "DataManager OddReal 2.0 iniciado."
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _now_iso() -> str:
        """
        Retorna timestamp UTC em formato ISO.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:
        """
        Converte valores textuais com segurança.
        """

        if value is None:

            return default

        value = str(
            value
        ).strip()

        return (
            value
            if value
            else default
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: Optional[float] = None,
    ) -> Optional[float]:
        """
        Converte um valor para float.
        """

        if value is None:

            return default

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # ==========================================================
    # VALIDAÇÃO
    # ==========================================================

    def validate_event(
        self,
        event: Dict[str, Any],
    ) -> bool:
        """
        Verifica se o evento possui estrutura mínima.
        """

        if not isinstance(
            event,
            dict,
        ):

            return False

        event_id = event.get(
            "id"
        )

        home_team = event.get(
            "home_team"
        )

        away_team = event.get(
            "away_team"
        )

        if not event_id:

            return False

        if not home_team:

            return False

        if not away_team:

            return False

        return True

    # ==========================================================
    # LIMPEZA
    # ==========================================================

    def clean_event(
        self,
        event: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Limpa e padroniza um evento.

        Os dados originais são preservados sempre que possível.
        """

        if not self.validate_event(
            event
        ):

            return None

        cleaned = deepcopy(
            event
        )

        cleaned["id"] = (
            self._safe_string(
                event.get(
                    "id"
                )
            )
        )

        cleaned["sport_key"] = (
            self._safe_string(
                event.get(
                    "sport_key"
                ),
                "unknown",
            )
        )

        cleaned["sport_title"] = (
            self._safe_string(
                event.get(
                    "sport_title"
                ),
                cleaned["sport_key"],
            )
        )

        cleaned["home_team"] = (
            self._safe_string(
                event.get(
                    "home_team"
                ),
                "Mandante",
            )
        )

        cleaned["away_team"] = (
            self._safe_string(
                event.get(
                    "away_team"
                ),
                "Visitante",
            )
        )

        cleaned["commence_time"] = (
            self._safe_string(
                event.get(
                    "commence_time"
                )
            )
        )

        bookmakers = event.get(
            "bookmakers",
            [],
        )

        if not isinstance(
            bookmakers,
            list,
        ):

            bookmakers = []

        cleaned["bookmakers"] = (
            bookmakers
        )

        cleaned["_processed_at"] = (
            self._now_iso()
        )

        return cleaned

    # ==========================================================
    # PROCESSAMENTO EM LOTE
    # ==========================================================

    def clean_events(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Limpa uma coleção de eventos.
        """

        if not isinstance(
            events,
            list,
        ):

            return []

        cleaned_events: List[
            Dict[str, Any]
        ] = []

        for event in events:

            try:

                cleaned = self.clean_event(
                    event
                )

                if cleaned is not None:

                    cleaned_events.append(
                        cleaned
                    )

            except Exception as exc:

                error(
                    "Erro ao limpar evento: "
                    f"{exc}"
                )

        self.last_clean_events = (
            deepcopy(
                cleaned_events
            )
        )

        self.last_processed_at = (
            self._now_iso()
        )

        return cleaned_events

    # ==========================================================
    # PREPARAÇÃO PARA ANÁLISE
    # ==========================================================

    def prepare_for_analysis(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Prepara os eventos para o Pipeline.

        Neste estágio não fazemos cálculos de odds.
        Apenas garantimos que os dados fundamentais
        estejam disponíveis.
        """

        cleaned_events = (
            self.clean_events(
                events
            )
        )

        prepared: List[
            Dict[str, Any]
        ] = []

        for event in cleaned_events:

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not bookmakers:

                continue

            prepared.append(
                event
            )

        info(
            "DataManager preparou "
            f"{len(prepared)} eventos "
            "para análise."
        )

        return prepared

    # ==========================================================
    # PREPARAÇÃO PARA IA
    # ==========================================================

    def prepare_for_ai(
        self,
        analyses: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Cria uma versão enxuta dos dados para a IA.

        Evita enviar informações desnecessárias e mantém
        os indicadores fundamentais da análise.
        """

        if not isinstance(
            analyses,
            list,
        ):

            return []

        ai_data: List[
            Dict[str, Any]
        ] = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):

                continue

            ai_data.append(
                {
                    "event_id": analysis.get(
                        "id"
                    ),

                    "sport": analysis.get(
                        "sport_title",
                        analysis.get(
                            "sport_key"
                        ),
                    ),

                    "home_team": analysis.get(
                        "home_team"
                    ),

                    "away_team": analysis.get(
                        "away_team"
                    ),

                    "odd": analysis.get(
                        "odd"
                    ),

                    "probability": analysis.get(
                        "probability"
                    ),

                    "expected_value": analysis.get(
                        "expected_value"
                    ),

                    "oddreal_index": analysis.get(
                        "oddreal_index"
                    ),

                    "confidence_level": analysis.get(
                        "confidence_level"
                    ),

                    "average_odd": analysis.get(
                        "average_odd"
                    ),

                    "market_variation": analysis.get(
                        "market_variation"
                    ),

                    "risk": analysis.get(
                        "risk"
                    ),

                    "is_value_bet": analysis.get(
                        "is_value_bet",
                        False,
                    ),
                }
            )

        return ai_data

    # ==========================================================
    # RESUMO
    # ==========================================================

    def summary(
        self,
        events: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Retorna um resumo do conjunto atual.
        """

        if events is None:

            events = (
                self.last_clean_events
            )

        if not isinstance(
            events,
            list,
        ):

            events = []

        sports = set()

        for event in events:

            if not isinstance(
                event,
                dict,
            ):

                continue

            sport = event.get(
                "sport_title",
                event.get(
                    "sport_key"
                ),
            )

            if sport:

                sports.add(
                    sport
                )

        return {

            "total_events": len(
                events
            ),

            "total_sports": len(
                sports
            ),

            "sports": sorted(
                sports
            ),

            "processed_at": (
                self.last_processed_at
            ),

        }

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna um snapshot seguro do estado atual.
        """

        return {

            "raw_events": deepcopy(
                self.last_raw_events
            ),

            "clean_events": deepcopy(
                self.last_clean_events
            ),

            "processed_at": (
                self.last_processed_at
            ),

            "summary": self.summary(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self,
    ) -> None:
        """
        Limpa o estado temporário do DataManager.
        """

        self.last_raw_events = []

        self.last_clean_events = []

        self.last_processed_at = None

        info(
            "DataManager resetado."
        )

    # ==========================================================
    # CICLO COMPLETO
    # ==========================================================

    def process(
        self,
        events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Executa o ciclo básico de gerenciamento de dados.

        Retorna dados brutos, limpos e preparados.
        """

        if not isinstance(
            events,
            list,
        ):

            events = []

        self.last_raw_events = (
            deepcopy(
                events
            )
        )

        clean_events = (
            self.clean_events(
                events
            )
        )

        analysis_events = (
            self.prepare_for_analysis(
                clean_events
            )
        )

        return {

            "raw_events": deepcopy(
                events
            ),

            "clean_events": clean_events,

            "analysis_events": (
                analysis_events
            ),

            "summary": self.summary(
                clean_events
            ),

        }


data_manager = DataManager()
