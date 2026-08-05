"""
OddReal 2.0
Analyzer — Motor de Análise de Odds

Responsabilidades:

- receber eventos processados pelo DataManager;
- trabalhar com todas as bookmakers recebidas pela API;
- não exigir bookmaker brasileiro;
- não depender de broker_maker;
- não eliminar bookmakers por lista fixa;
- agrupar odds por evento/mercado/resultado;
- identificar a melhor odd disponível;
- calcular odd média;
- calcular probabilidade implícita;
- calcular probabilidade de mercado normalizada;
- calcular margem/vigorish do mercado;
- calcular valor esperado (EV);
- identificar Value Bets;
- calcular Índice OddReal;
- calcular nível de confiança;
- classificar risco;
- produzir registros prontos para interface;
- produzir dados compatíveis com prepare_for_ai() do DataManager.

IMPORTANTE:

Este módulo NÃO consulta diretamente a The Odds API.

Fluxo esperado:

    modules/api.py
            ↓
    modules/data_manager.py
            ↓
    modules/analyzer.py
            ↓
    interface / OddsEngine / IA

O Analyzer utiliza exclusivamente os dados que recebeu.

Nenhuma bookmaker específica é obrigatória.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Tuple

from modules.logger import info, warning, error


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

MIN_ODD = 1.01
MAX_ODD = 1000.0

# Quantidade mínima de bookmakers diferentes para que
# a comparação seja considerada robusta.
MIN_BOOKMAKERS_FOR_COMPARISON = 2

# Peso dos componentes do Índice OddReal.
#
# O índice não representa probabilidade.
# É um indicador interno de qualidade/oportunidade.
WEIGHT_VALUE = 0.45
WEIGHT_ODD_ADVANTAGE = 0.30
WEIGHT_MARKET_CONFIDENCE = 0.25

# Limites para classificação.
VALUE_BET_THRESHOLD = 0.0

CONFIDENCE_HIGH = 75.0
CONFIDENCE_MEDIUM = 55.0

RISK_LOW = 25.0
RISK_MEDIUM = 50.0
RISK_HIGH = 75.0


class Analyzer:
    """
    Motor central de análise do OddReal 2.0.

    O Analyzer recebe dados já processados pelo DataManager
    e transforma as odds disponíveis em informações analíticas.

    Nenhuma bookmaker é obrigatória.
    """

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(self) -> None:

        self.last_events: List[
            Dict[str, Any]
        ] = []

        self.last_records: List[
            Dict[str, Any]
        ] = []

        self.last_analyses: List[
            Dict[str, Any]
        ] = []

        self.last_processed_at: Optional[
            str
        ] = None

        info(
            "Analyzer OddReal 2.0 iniciado."
        )

    # ======================================================
    # UTILITÁRIOS
    # ======================================================

    @staticmethod
    def _now_iso() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _safe_string(
        value: Any,
        default: str = "",
    ) -> str:

        if value is None:
            return default

        try:

            result = str(
                value
            ).strip()

        except Exception:

            return default

        return (
            result
            if result
            else default
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: Optional[float] = None,
    ) -> Optional[float]:

        if value is None:
            return default

        try:

            result = float(
                value
            )

            if result != result:
                return default

            if result in (
                float("inf"),
                float("-inf"),
            ):
                return default

            return result

        except (
            TypeError,
            ValueError,
        ):

            return default

    @staticmethod
    def _clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    @staticmethod
    def _round(
        value: Optional[float],
        digits: int = 4,
    ) -> Optional[float]:

        if value is None:
            return None

        return round(
            value,
            digits,
        )

    # ======================================================
    # ODD
    # ======================================================

    @classmethod
    def _valid_odd(
        cls,
        value: Any,
    ) -> Optional[float]:

        odd = cls._safe_float(
            value
        )

        if odd is None:
            return None

        if odd < MIN_ODD:
            return None

        if odd > MAX_ODD:
            return None

        return odd

    # ======================================================
    # PROBABILIDADE IMPLÍCITA
    # ======================================================

    @classmethod
    def implied_probability(
        cls,
        odd: Any,
    ) -> Optional[float]:
        """
        Converte uma odd decimal em probabilidade implícita.

        Exemplo:

            odd = 2.00
            probabilidade = 50%

        Retorno em escala decimal:

            0.50
        """

        valid_odd = cls._valid_odd(
            odd
        )

        if valid_odd is None:
            return None

        return 1.0 / valid_odd

    # ======================================================
    # AGRUPAMENTO
    # ======================================================

    @staticmethod
    def _record_group_key(
        record: Dict[str, Any],
    ) -> Tuple[str, str, str]:
        """
        Agrupa por:

            evento
            mercado
            resultado
        """

        event_id = str(
            record.get(
                "event_id",
                record.get(
                    "id",
                    "",
                ),
            )
        )

        market_key = str(
            record.get(
                "market_key",
                "",
            )
        )

        outcome_name = str(
            record.get(
                "outcome_name",
                "",
            )
        )

        return (
            event_id,
            market_key,
            outcome_name,
        )

    # ======================================================
    # NORMALIZAÇÃO DOS RECORDS
    # ======================================================

    @classmethod
    def _normalize_record(
        cls,
        record: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        if not isinstance(
            record,
            dict,
        ):
            return None

        odd = cls._valid_odd(
            record.get(
                "odd"
            )
        )

        if odd is None:
            return None

        event_id = cls._safe_string(
            record.get(
                "event_id",
                record.get(
                    "id"
                ),
            )
        )

        market_key = cls._safe_string(
            record.get(
                "market_key"
            )
        )

        outcome_name = cls._safe_string(
            record.get(
                "outcome_name"
            )
        )

        bookmaker_key = cls._safe_string(
            record.get(
                "bookmaker_key"
            )
        )

        bookmaker = cls._safe_string(
            record.get(
                "bookmaker",
                bookmaker_key,
            )
        )

        if not event_id:
            return None

        if not market_key:
            return None

        if not outcome_name:
            return None

        if not bookmaker_key:
            bookmaker_key = (
                bookmaker.lower()
            )

        normalized = deepcopy(
            record
        )

        normalized[
            "event_id"
        ] = event_id

        normalized[
            "market_key"
        ] = market_key

        normalized[
            "outcome_name"
        ] = outcome_name

        normalized[
            "bookmaker_key"
        ] = bookmaker_key

        normalized[
            "bookmaker"
        ] = bookmaker

        normalized[
            "odd"
        ] = odd

        normalized[
            "bookmaker_allowed"
        ] = bool(
            record.get(
                "bookmaker_allowed",
                False,
            )
        )

        return normalized

    # ======================================================
    # FILTRO DE RECORDS
    # ======================================================

    @classmethod
    def _normalize_records(
        cls,
        records: Iterable[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        normalized_records = []

        for record in records:

            try:

                normalized = (
                    cls._normalize_record(
                        record
                    )
                )

                if normalized is not None:

                    normalized_records.append(
                        normalized
                    )

            except Exception as exc:

                error(
                    "Erro ao normalizar "
                    f"registro de odd: {exc}"
                )

        return normalized_records

    # ======================================================
    # BOOKMAKERS ÚNICAS
    # ======================================================

    @staticmethod
    def _unique_bookmakers(
        records: List[
            Dict[str, Any]
        ],
    ) -> List[str]:

        bookmakers = set()

        for record in records:

            key = record.get(
                "bookmaker_key"
            )

            if key:

                bookmakers.add(
                    str(key)
                )

        return sorted(
            bookmakers
        )

    # ======================================================
    # ODDS
    # ======================================================

    @classmethod
    def _odds(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> List[float]:

        odds = []

        for record in records:

            odd = cls._valid_odd(
                record.get(
                    "odd"
                )
            )

            if odd is not None:

                odds.append(
                    odd
                )

        return odds

    # ======================================================
    # MELHOR ODD
    # ======================================================

    @classmethod
    def _best_record(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, Any]
    ]:

        valid_records = []

        for record in records:

            odd = cls._valid_odd(
                record.get(
                    "odd"
                )
            )

            if odd is None:
                continue

            valid_records.append(
                record
            )

        if not valid_records:

            return None

        return max(
            valid_records,
            key=lambda item: float(
                item.get(
                    "odd"
                )
            ),
        )

    # ======================================================
    # ODD MÉDIA
    # ======================================================

    @classmethod
    def _average_odd(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Optional[float]:

        odds = cls._odds(
            records
        )

        if not odds:
            return None

        return mean(
            odds
        )

    # ======================================================
    # MEDIANA
    # ======================================================

    @classmethod
    def _median_odd(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Optional[float]:

        odds = cls._odds(
            records
        )

        if not odds:
            return None

        return median(
            odds
        )

    # ======================================================
    # VARIAÇÃO DA ODD
    # ======================================================

    @classmethod
    def _market_variation(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Optional[float]:

        odds = cls._odds(
            records
        )

        if len(odds) < 2:

            return 0.0 if odds else None

        minimum = min(
            odds
        )

        maximum = max(
            odds
        )

        if minimum <= 0:
            return None

        variation = (
            (maximum - minimum)
            / minimum
        ) * 100.0

        return cls._round(
            variation,
            2,
        )

    # ======================================================
    # MARGEM DE MERCADO
    # ======================================================

    @classmethod
    def market_margin(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Optional[float]:
        """
        Calcula a margem implícita do mercado.

        Para um mercado com resultados:

            P1 + P2 + P3

        Se a soma for 1.06:

            margem = 6%

        Retorno em percentual.
        """

        probabilities = []

        for record in records:

            probability = (
                cls.implied_probability(
                    record.get(
                        "odd"
                    )
                )
            )

            if probability is not None:

                probabilities.append(
                    probability
                )

        if not probabilities:

            return None

        total = sum(
            probabilities
        )

        margin = (
            total - 1.0
        ) * 100.0

        return cls._round(
            margin,
            2,
        )

    # ======================================================
    # PROBABILIDADE NORMALIZADA
    # ======================================================

    @classmethod
    def normalized_market_probability(
        cls,
        records: List[
            Dict[str, Any]
        ],
        outcome_name: str,
    ) -> Optional[float]:
        """
        Calcula a probabilidade de mercado normalizada
        para um resultado.

        Remove a margem implícita do mercado.

        Retorno em escala decimal.
        """

        probabilities = {}

        for record in records:

            name = cls._safe_string(
                record.get(
                    "outcome_name"
                )
            )

            odd = cls.implied_probability(
                record.get(
                    "odd"
                )
            )

            if not name or odd is None:
                continue

            # Para cada resultado, usamos a melhor odd
            # disponível entre as bookmakers.

            current = probabilities.get(
                name
            )

            if current is None:

                probabilities[
                    name
                ] = odd

            else:

                # Menor probabilidade implícita
                # corresponde à maior odd.
                probabilities[
                    name
                ] = min(
                    current,
                    odd,
                )

        if not probabilities:
            return None

        total = sum(
            probabilities.values()
        )

        if total <= 0:
            return None

        target = probabilities.get(
            outcome_name
        )

        if target is None:
            return None

        return target / total

    # ======================================================
    # PROBABILIDADE CONSENSUAL
    # ======================================================

    @classmethod
    def consensus_probability(
        cls,
        records: List[
            Dict[str, Any]
        ],
        outcome_name: str,
    ) -> Optional[float]:
        """
        Calcula uma estimativa consensual usando as odds
        disponíveis para o resultado.

        A média é calculada sobre as probabilidades implícitas
        das bookmakers disponíveis.
        """

        values = []

        for record in records:

            if (
                cls._safe_string(
                    record.get(
                        "outcome_name"
                    )
                )
                != outcome_name
            ):
                continue

            probability = (
                cls.implied_probability(
                    record.get(
                        "odd"
                    )
                )
            )

            if probability is not None:

                values.append(
                    probability
                )

        if not values:
            return None

        return mean(
            values
        )

    # ======================================================
    # MELHOR ODDS POR RESULTADO
    # ======================================================

    @classmethod
    def _best_odds_by_outcome(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:

        result: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for record in records:

            outcome = cls._safe_string(
                record.get(
                    "outcome_name"
                )
            )

            odd = cls._valid_odd(
                record.get(
                    "odd"
                )
            )

            if not outcome or odd is None:
                continue

            current = result.get(
                outcome
            )

            if (
                current is None
                or odd
                > float(
                    current.get(
                        "odd",
                        0,
                    )
                )
            ):

                result[
                    outcome
                ] = record

        return result

    # ======================================================
    # EV
    # ======================================================

    @classmethod
    def expected_value(
        cls,
        odd: Any,
        probability: Any,
    ) -> Optional[float]:
        """
        Calcula Expected Value.

        Fórmula:

            EV = (odd × probabilidade) - 1

        Exemplo:

            odd = 2.20
            probabilidade = 0.50

            EV = 2.20 × 0.50 - 1
               = 0.10

        Retorno:

            0.10 = +10%
        """

        valid_odd = cls._valid_odd(
            odd
        )

        valid_probability = (
            cls._safe_float(
                probability
            )
        )

        if (
            valid_odd is None
            or valid_probability is None
        ):
            return None

        if (
            valid_probability <= 0
            or valid_probability >= 1
        ):
            return None

        ev = (
            valid_odd
            * valid_probability
        ) - 1.0

        return cls._round(
            ev,
            4,
        )

    # ======================================================
    # ADVANTAGE DA ODD
    # ======================================================

    @classmethod
    def odd_advantage(
        cls,
        odd: Any,
        average_odd: Any,
    ) -> Optional[float]:
        """
        Mede quanto a melhor odd está acima da odd média.

        Retorno em percentual.
        """

        valid_odd = cls._valid_odd(
            odd
        )

        valid_average = cls._valid_odd(
            average_odd
        )

        if (
            valid_odd is None
            or valid_average is None
        ):
            return None

        if valid_average <= 0:
            return None

        advantage = (
            (
                valid_odd
                / valid_average
            )
            - 1.0
        ) * 100.0

        return cls._round(
            advantage,
            2,
        )

    # ======================================================
    # CONFIANÇA
    # ======================================================

    @classmethod
    def confidence_score(
        cls,
        ev: Optional[float],
        odd_advantage: Optional[float],
        bookmaker_count: int,
        market_variation: Optional[float],
    ) -> float:
        """
        Calcula uma pontuação de confiança de 0 a 100.

        Componentes:

        - EV;
        - vantagem da odd;
        - quantidade de bookmakers;
        - estabilidade/variação do mercado.

        É uma métrica interna do OddReal.
        Não representa garantia de resultado.
        """

        ev_component = 0.0

        if ev is not None:

            ev_component = cls._clamp(
                ev * 500.0,
                0.0,
                100.0,
            )

        advantage_component = 0.0

        if odd_advantage is not None:

            advantage_component = cls._clamp(
                odd_advantage * 10.0,
                0.0,
                100.0,
            )

        if bookmaker_count <= 0:

            bookmaker_component = 0.0

        else:

            bookmaker_component = cls._clamp(
                (
                    bookmaker_count
                    / 5.0
                )
                * 100.0,
                0.0,
                100.0,
            )

        if market_variation is None:

            stability_component = 50.0

        else:

            # Pequena variação = maior estabilidade.
            stability_component = cls._clamp(
                100.0
                - (
                    market_variation
                    * 5.0
                ),
                0.0,
                100.0,
            )

        score = (
            ev_component * 0.40
            + advantage_component * 0.25
            + bookmaker_component * 0.15
            + stability_component * 0.20
        )

        return cls._round(
            cls._clamp(
                score
            ),
            2,
        ) or 0.0

    # ======================================================
    # NÍVEL DE CONFIANÇA
    # ======================================================

    @staticmethod
    def confidence_level(
        score: float,
    ) -> str:

        if score >= CONFIDENCE_HIGH:

            return "Alta"

        if score >= CONFIDENCE_MEDIUM:

            return "Média"

        return "Baixa"

    # ======================================================
    # RISCO
    # ======================================================

    @classmethod
    def risk_score(
        cls,
        ev: Optional[float],
        bookmaker_count: int,
        market_variation: Optional[float],
        confidence: float,
    ) -> float:
        """
        Calcula risco interno de 0 a 100.

        Quanto maior:

            maior o risco relativo da oportunidade.

        Não é uma probabilidade de perda.
        """

        risk = 50.0

        # Poucas fontes de preço aumentam risco.
        if bookmaker_count <= 1:

            risk += 20.0

        elif bookmaker_count == 2:

            risk += 10.0

        elif bookmaker_count >= 5:

            risk -= 10.0

        # Mercado muito disperso.
        if market_variation is not None:

            risk += cls._clamp(
                market_variation * 2.0,
                0.0,
                25.0,
            )

        # EV negativo aumenta risco.
        if ev is not None:

            if ev < 0:

                risk += cls._clamp(
                    abs(ev) * 100.0,
                    0.0,
                    25.0,
                )

            elif ev > 0:

                risk -= cls._clamp(
                    ev * 50.0,
                    0.0,
                    15.0,
                )

        # Confiança reduz risco.
        risk -= (
            confidence - 50.0
        ) * 0.20

        return cls._round(
            cls._clamp(
                risk
            ),
            2,
        ) or 0.0

    # ======================================================
    # CLASSIFICAÇÃO DE RISCO
    # ======================================================

    @staticmethod
    def risk_level(
        score: float,
    ) -> str:

        if score <= RISK_LOW:

            return "Baixo"

        if score <= RISK_MEDIUM:

            return "Moderado"

        if score <= RISK_HIGH:

            return "Alto"

        return "Muito alto"

    # ======================================================
    # ÍNDICE ODDREAL
    # ======================================================

    @classmethod
    def oddreal_index(
        cls,
        ev: Optional[float],
        odd_advantage: Optional[float],
        confidence: float,
    ) -> float:
        """
        Calcula o Índice OddReal de 0 a 100.

        Componentes:

            EV
            vantagem da odd
            confiança

        O índice é uma métrica proprietária do sistema.
        """

        if ev is None:
            ev_component = 0.0

        else:

            ev_component = cls._clamp(
                ev * 500.0,
                0.0,
                100.0,
            )

        if odd_advantage is None:

            advantage_component = 0.0

        else:

            advantage_component = cls._clamp(
                odd_advantage * 10.0,
                0.0,
                100.0,
            )

        index = (
            ev_component
            * WEIGHT_VALUE
            + advantage_component
            * WEIGHT_ODD_ADVANTAGE
            + confidence
            * WEIGHT_MARKET_CONFIDENCE
        )

        return cls._round(
            cls._clamp(
                index
            ),
            2,
        ) or 0.0

    # ======================================================
    # CLASSIFICAÇÃO DA OPORTUNIDADE
    # ======================================================

    @staticmethod
    def opportunity_label(
        ev: Optional[float],
        index: float,
    ) -> str:

        if ev is None:

            return "Sem dados"

        if ev <= 0:

            return "Sem valor"

        if index >= 75:

            return "Value Bet forte"

        if index >= 55:

            return "Value Bet"

        return "Oportunidade moderada"

    # ======================================================
    # ANÁLISE DE UM GRUPO
    # ======================================================

    @classmethod
    def analyze_group(
        cls,
        records: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Analisa todas as bookmakers para um determinado
        evento + mercado + resultado.
        """

        if not records:

            return []

        first = records[0]

        event_id = first.get(
            "event_id"
        )

        market_key = first.get(
            "market_key"
        )

        outcome_name = first.get(
            "outcome_name"
        )

        bookmakers = cls._unique_bookmakers(
            records
        )

        best_record = cls._best_record(
            records
        )

        if best_record is None:

            return []

        best_odd = cls._valid_odd(
            best_record.get(
                "odd"
            )
        )

        if best_odd is None:

            return []

        average_odd = cls._average_odd(
            records
        )

        median_odd = cls._median_odd(
            records
        )

        variation = cls._market_variation(
            records
        )

        margin = cls.market_margin(
            records
        )

        normalized_probability = (
            cls.normalized_market_probability(
                records,
                str(
                    outcome_name
                ),
            )
        )

        consensus_probability = (
            cls.consensus_probability(
                records,
                str(
                    outcome_name
                ),
            )
        )

        # Para cálculo de EV, priorizamos a probabilidade
        # normalizada do mercado.
        #
        # Se não houver dados suficientes, utilizamos
        # a probabilidade consensual.

        probability = (
            normalized_probability
            if normalized_probability
            is not None
            else consensus_probability
        )

        ev = cls.expected_value(
            best_odd,
            probability,
        )

        advantage = cls.odd_advantage(
            best_odd,
            average_odd,
        )

        confidence = cls.confidence_score(
            ev=ev,
            odd_advantage=advantage,
            bookmaker_count=len(
                bookmakers
            ),
            market_variation=variation,
        )

        confidence_text = (
            cls.confidence_level(
                confidence
            )
        )

        risk = cls.risk_score(
            ev=ev,
            bookmaker_count=len(
                bookmakers
            ),
            market_variation=variation,
            confidence=confidence,
        )

        risk_text = cls.risk_level(
            risk
        )

        oddreal = cls.oddreal_index(
            ev=ev,
            odd_advantage=advantage,
            confidence=confidence,
        )

        label = cls.opportunity_label(
            ev=ev,
            index=oddreal,
        )

        result = deepcopy(
            best_record
        )

        # --------------------------------------------------
        # CAMPOS ANALÍTICOS
        # --------------------------------------------------

        result[
            "best_odd"
        ] = cls._round(
            best_odd,
            4,
        )

        result[
            "best_bookmaker_key"
        ] = best_record.get(
            "bookmaker_key"
        )

        result[
            "best_bookmaker"
        ] = best_record.get(
            "bookmaker"
        )

        result[
            "average_odd"
        ] = cls._round(
            average_odd,
            4,
        )

        result[
            "median_odd"
        ] = cls._round(
            median_odd,
            4,
        )

        result[
            "market_variation"
        ] = variation

        result[
            "market_margin"
        ] = margin

        result[
            "probability"
        ] = cls._round(
            probability,
            6,
        )

        result[
            "normalized_probability"
        ] = cls._round(
            normalized_probability,
            6,
        )

        result[
            "consensus_probability"
        ] = cls._round(
            consensus_probability,
            6,
        )

        result[
            "expected_value"
        ] = ev

        result[
            "odd_advantage"
        ] = advantage

        result[
            "confidence"
        ] = confidence

        result[
            "confidence_level"
        ] = confidence_text

        result[
            "risk_score"
        ] = risk

        result[
            "risk"
        ] = risk_text

        result[
            "oddreal_index"
        ] = oddreal

        result[
            "opportunity"
        ] = label

        result[
            "is_value_bet"
        ] = bool(
            ev is not None
            and ev > VALUE_BET_THRESHOLD
        )

        result[
            "bookmaker_count"
        ] = len(
            bookmakers
        )

        result[
            "bookmakers"
        ] = bookmakers

        result[
            "bookmaker_odds"
        ] = [
            {
                "bookmaker_key": item.get(
                    "bookmaker_key"
                ),
                "bookmaker": item.get(
                    "bookmaker"
                ),
                "odd": item.get(
                    "odd"
                ),
            }
            for item in records
        ]

        result[
            "analyzed_at"
        ] = cls._now_iso()

        return [result]

    # ======================================================
    # ANÁLISE DOS RECORDS
    # ======================================================

    def analyze_records(
        self,
        records: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        if not isinstance(
            records,
            list,
        ):

            warning(
                "Analyzer recebeu records "
                "em formato inválido."
            )

            return []

        normalized = (
            self._normalize_records(
                records
            )
        )

        self.last_records = deepcopy(
            normalized
        )

        if not normalized:

            warning(
                "Analyzer não recebeu "
                "registros de odds válidos."
            )

            self.last_analyses = []

            return []

        grouped: Dict[
            Tuple[str, str, str],
            List[Dict[str, Any]]
        ] = defaultdict(list)

        for record in normalized:

            key = (
                self._record_group_key(
                    record
                )
            )

            grouped[
                key
            ].append(
                record
            )

        analyses = []

        for key, group in grouped.items():

            try:

                result = (
                    self.analyze_group(
                        group
                    )
                )

                analyses.extend(
                    result
                )

            except Exception as exc:

                error(
                    "Erro ao analisar grupo "
                    f"{key}: {exc}"
                )

        self.last_analyses = deepcopy(
            analyses
        )

        self.last_processed_at = (
            self._now_iso()
        )

        info(
            "Analyzer processou "
            f"{len(normalized)} registros "
            f"e produziu "
            f"{len(analyses)} análises."
        )

        return analyses

    # ======================================================
    # ANÁLISE DIRETA DE EVENTOS
    # ======================================================

    def analyze_events(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Recebe eventos preparados pelo DataManager.

        Esta função também consegue extrair os registros
        diretamente dos bookmakers presentes nos eventos.
        """

        if not isinstance(
            events,
            list,
        ):

            warning(
                "Analyzer recebeu eventos "
                "em formato inválido."
            )

            return []

        self.last_events = deepcopy(
            events
        )

        records = []

        for event in events:

            if not isinstance(
                event,
                dict,
            ):
                continue

            bookmakers = event.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):
                continue

            for bookmaker in bookmakers:

                if not isinstance(
                    bookmaker,
                    dict,
                ):
                    continue

                bookmaker_key = (
                    bookmaker.get(
                        "_normalized_key"
                    )
                    or bookmaker.get(
                        "key"
                    )
                    or bookmaker.get(
                        "title"
                    )
                )

                bookmaker_name = (
                    bookmaker.get(
                        "_display_name"
                    )
                    or bookmaker.get(
                        "title"
                    )
                    or bookmaker_key
                )

                markets = bookmaker.get(
                    "markets",
                    [],
                )

                if not isinstance(
                    markets,
                    list,
                ):
                    continue

                for market in markets:

                    if not isinstance(
                        market,
                        dict,
                    ):
                        continue

                    market_key = (
                        market.get(
                            "key"
                        )
                    )

                    outcomes = market.get(
                        "outcomes",
                        [],
                    )

                    if not isinstance(
                        outcomes,
                        list,
                    ):
                        continue

                    for outcome in outcomes:

                        if not isinstance(
                            outcome,
                            dict,
                        ):
                            continue

                        odd = self._valid_odd(
                            outcome.get(
                                "price"
                            )
                        )

                        outcome_name = (
                            outcome.get(
                                "name"
                            )
                        )

                        if (
                            odd is None
                            or not outcome_name
                        ):
                            continue

                        record = {

                            "event_id": event.get(
                                "id"
                            ),

                            "id": event.get(
                                "id"
                            ),

                            "sport_key": event.get(
                                "sport_key"
                            ),

                            "sport_title": event.get(
                                "sport_title"
                            ),

                            "home_team": event.get(
                                "home_team"
                            ),

                            "away_team": event.get(
                                "away_team"
                            ),

                            "commence_time": event.get(
                                "commence_time"
                            ),

                            "bookmaker_key": (
                                str(
                                    bookmaker_key
                                    or ""
                                )
                            ),

                            "bookmaker": (
                                str(
                                    bookmaker_name
                                    or ""
                                )
                            ),

                            "bookmaker_allowed": bool(
                                bookmaker.get(
                                    "_allowed",
                                    False,
                                )
                            ),

                            "market_key": (
                                str(
                                    market_key
                                    or ""
                                )
                            ),

                            "outcome_name": (
                                str(
                                    outcome_name
                                )
                            ),

                            "odd": odd,
                        }

                        if "point" in outcome:

                            point = self._safe_float(
                                outcome.get(
                                    "point"
                                )
                            )

                            if point is not None:

                                record[
                                    "point"
                                ] = point

                        records.append(
                            record
                        )

        return self.analyze_records(
            records
        )

    # ======================================================
    # ANÁLISE COMPATÍVEL COM DATAMANAGER
    # ======================================================

    def analyze_data_manager_output(
        self,
        processed_data: Dict[
            str,
            Any,
        ],
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Recebe diretamente o resultado de:

            DataManager.process()

        Esperado:

            {
                "raw_events": ...,
                "clean_events": ...,
                "analysis_events": ...,
                "analysis_records": ...,
                "summary": ...
            }
        """

        if not isinstance(
            processed_data,
            dict,
        ):

            warning(
                "Saída do DataManager "
                "em formato inválido."
            )

            return []

        records = (
            processed_data.get(
                "analysis_records",
                [],
            )
        )

        if isinstance(
            records,
            list,
        ) and records:

            return self.analyze_records(
                records
            )

        events = (
            processed_data.get(
                "analysis_events",
                []
            )
        )

        if isinstance(
            events,
            list,
        ):

            return self.analyze_events(
                events
            )

        return []

    # ======================================================
    # MELHOR OPORTUNIDADE
    # ======================================================

    def best_opportunities(
        self,
        analyses: Optional[
            List[
                Dict[str, Any]
            ]
        ] = None,
        limit: int = 20,
    ) -> List[
        Dict[str, Any]
    ]:

        if analyses is None:

            analyses = (
                self.last_analyses
            )

        if not isinstance(
            analyses,
            list,
        ):

            return []

        valid = []

        for analysis in analyses:

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            if not analysis.get(
                "is_value_bet",
                False,
            ):
                continue

            valid.append(
                analysis
            )

        valid.sort(
            key=lambda item: float(
                item.get(
                    "oddreal_index",
                    0,
                )
                or 0
            ),
            reverse=True,
        )

        return deepcopy(
            valid[
                :max(
                    0,
                    int(limit),
                )
            ]
        )

    # ======================================================
    # FILTRO POR ESPORTE
    # ======================================================

    def filter_by_sport(
        self,
        analyses: List[
            Dict[str, Any]
        ],
        sport: str,
    ) -> List[
        Dict[str, Any]
    ]:

        if not sport:

            return deepcopy(
                analyses
            )

        target = sport.strip().lower()

        return [
            deepcopy(
                item
            )
            for item in analyses
            if str(
                item.get(
                    "sport_key",
                    item.get(
                        "sport_title",
                        "",
                    ),
                )
            ).strip().lower()
            == target
        ]

    # ======================================================
    # FILTRO VALUE BET
    # ======================================================

    def filter_value_bets(
        self,
        analyses: List[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        return [
            deepcopy(
                item
            )
            for item in analyses
            if item.get(
                "is_value_bet",
                False,
            )
        ]

    # ======================================================
    # RESUMO
    # ======================================================

    def summary(
        self,
        analyses: Optional[
            List[
                Dict[str, Any]
            ]
        ] = None,
    ) -> Dict[str, Any]:

        if analyses is None:

            analyses = (
                self.last_analyses
            )

        if not isinstance(
            analyses,
            list,
        ):

            analyses = []

        value_bets = [
            item
            for item in analyses
            if isinstance(
                item,
                dict,
            )
            and item.get(
                "is_value_bet",
                False,
            )
        ]

        bookmakers = set()

        sports = set()

        events = set()

        positive_ev = []

        indexes = []

        for item in analyses:

            if not isinstance(
                item,
                dict,
            ):
                continue

            bookmaker_key = item.get(
                "best_bookmaker_key"
            )

            if bookmaker_key:

                bookmakers.add(
                    str(
                        bookmaker_key
                    )
                )

            sport = item.get(
                "sport_key",
                item.get(
                    "sport_title"
                ),
            )

            if sport:

                sports.add(
                    str(
                        sport
                    )
                )

            event_id = item.get(
                "event_id"
            )

            if event_id:

                events.add(
                    str(
                        event_id
                    )
                )

            ev = self._safe_float(
                item.get(
                    "expected_value"
                )
            )

            if ev is not None:

                if ev > 0:

                    positive_ev.append(
                        ev
                    )

            index = self._safe_float(
                item.get(
                    "oddreal_index"
                )
            )

            if index is not None:

                indexes.append(
                    index
                )

        average_ev = (
            mean(
                positive_ev
            )
            if positive_ev
            else 0.0
        )

        average_index = (
            mean(
                indexes
            )
            if indexes
            else 0.0
        )

        return {

            "total_analyses": len(
                analyses
            ),

            "value_bets": len(
                value_bets
            ),

            "total_events": len(
                events
            ),

            "total_sports": len(
                sports
            ),

            "sports": sorted(
                sports
            ),

            "bookmakers": sorted(
                bookmakers
            ),

            "total_bookmakers": len(
                bookmakers
            ),

            "average_positive_ev": (
                self._round(
                    average_ev,
                    4,
                )
            ),

            "average_oddreal_index": (
                self._round(
                    average_index,
                    2,
                )
            ),

            "processed_at": (
                self.last_processed_at
            ),
        }

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return {

            "events": deepcopy(
                self.last_events
            ),

            "records": deepcopy(
                self.last_records
            ),

            "analyses": deepcopy(
                self.last_analyses
            ),

            "summary": self.summary(),

            "processed_at": (
                self.last_processed_at
            ),
        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(
        self,
    ) -> None:

        self.last_events = []

        self.last_records = []

        self.last_analyses = []

        self.last_processed_at = None

        info(
            "Analyzer resetado."
        )

    # ======================================================
    # PROCESSAMENTO COMPLETO
    # ======================================================

    def process(
        self,
        data: Any,
    ) -> Dict[str, Any]:
        """
        Método principal.

        Aceita:

        1. lista de registros de odds;

        2. lista de eventos;

        3. resultado do DataManager.process().
        """

        try:

            # --------------------------------------------------
            # DICIONÁRIO DO DATAMANAGER
            # --------------------------------------------------

            if isinstance(
                data,
                dict,
            ):

                analyses = (
                    self.analyze_data_manager_output(
                        data
                    )
                )

            # --------------------------------------------------
            # LISTA
            # --------------------------------------------------

            elif isinstance(
                data,
                list,
            ):

                # Detecta se é lista de records de odds.
                #
                # Os records do DataManager possuem
                # "outcome_name" e "odd".

                looks_like_records = any(
                    isinstance(
                        item,
                        dict,
                    )
                    and (
                        "outcome_name"
                        in item
                    )
                    and (
                        "odd"
                        in item
                    )
                    for item in data
                )

                if looks_like_records:

                    analyses = (
                        self.analyze_records(
                            data
                        )
                    )

                else:

                    analyses = (
                        self.analyze_events(
                            data
                        )
                    )

            else:

                warning(
                    "Analyzer recebeu "
                    "tipo de dados não suportado."
                )

                analyses = []

            self.last_analyses = deepcopy(
                analyses
            )

            self.last_processed_at = (
                self._now_iso()
            )

            return {

                "analyses": deepcopy(
                    analyses
                ),

                "value_bets": (
                    self.best_opportunities(
                        analyses
                    )
                ),

                "summary": self.summary(
                    analyses
                ),

                "processed_at": (
                    self.last_processed_at
                ),
            }

        except Exception as exc:

            error(
                "Erro durante processamento "
                f"do Analyzer: {exc}"
            )

            return {

                "analyses": [],

                "value_bets": [],

                "summary": self.summary(
                    []
                ),

                "processed_at": (
                    self.last_processed_at
                ),

                "error": str(
                    exc
                ),
            }


# ==========================================================
# INSTÂNCIA GLOBAL
# ==========================================================

analyzer = Analyzer()


# ==========================================================
# EXPORTAÇÃO
# ==========================================================

__all__ = [
    "Analyzer",
    "analyzer",
]

                
            
