"""
OddReal 2.0
modules/data_manager.py

Gerenciamento completo do ciclo de dados:
- coleta
- limpeza
- padronização
- armazenamento
- histórico
- preparação para IA
"""

import os
import json
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path

from modules.config import (
    RAW_DATA_PATH,
    CLEAN_DATA_PATH,
    HISTORY_PATH
)


class DataManager:
    """
    Controlador central do fluxo de dados do OddReal.
    """


    def __init__(self):

        self.raw_path = Path(RAW_DATA_PATH)
        self.clean_path = Path(CLEAN_DATA_PATH)
        self.history_path = Path(HISTORY_PATH)

        self.create_directories()


    # ==================================================
    # CRIAÇÃO DAS PASTAS
    # ==================================================

    def create_directories(self):

        """
        Garante que todas as estruturas existam.
        """

        for folder in [
            self.raw_path,
            self.clean_path,
            self.history_path
        ]:
            folder.mkdir(
                parents=True,
                exist_ok=True
            )


    # ==================================================
    # COLETA E ARMAZENAMENTO BRUTO
    # ==================================================

    def save_raw_data(
        self,
        data,
        filename="odds_raw.json"
    ):

        """
        Salva resposta original da API.
        Mantém histórico sem alteração.
        """

        filepath = self.raw_path / filename


        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


        return filepath



    # ==================================================
    # LIMPEZA DOS DADOS
    # ==================================================

    def clean_data(
        self,
        data
    ):

        """
        Remove dados inválidos
        e prepara estrutura.
        """


        if not data:
            return []


        cleaned = []


        for event in data:


            if not isinstance(event, dict):
                continue


            if (
                "home_team" not in event
                or
                "away_team" not in event
            ):
                continue



            normalized = {

                "event_id":
                    self.generate_id(event),

                "home_team":
                    self.normalize_text(
                        event.get("home_team")
                    ),

                "away_team":
                    self.normalize_text(
                        event.get("away_team")
                    ),

                "sport":
                    event.get(
                        "sport",
                        "unknown"
                    ),

                "league":
                    event.get(
                        "league",
                        "unknown"
                    ),

                "timestamp":
                    datetime.utcnow().isoformat(),

                "odds":
                    event.get(
                        "odds",
                        {}
                    )
            }


            cleaned.append(
                normalized
            )


        return cleaned



    # ==================================================
    # PADRONIZAÇÃO DE TEXTO
    # ==================================================

    def normalize_text(
        self,
        text
    ):

        """
        Padroniza nomes.
        """

        if not text:
            return None


        return (
            str(text)
            .strip()
            .title()
        )



    # ==================================================
    # GERAÇÃO DE IDENTIFICADOR ÚNICO
    # ==================================================

    def generate_id(
        self,
        event
    ):

        """
        Cria hash único para cada partida.
        """

        raw = (
            str(
                event.get(
                    "home_team"
                )
            )
            +
            str(
                event.get(
                    "away_team"
                )
            )
        )


        return hashlib.md5(
            raw.encode()
        ).hexdigest()



    # ==================================================
    # SALVAR DADOS LIMPOS
    # ==================================================

    def save_clean_data(
        self,
        data,
        filename="odds_clean.json"
    ):


        filepath = (
            self.clean_path /
            filename
        )


        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


        return filepath



    # ==================================================
    # CONTROLE DE HISTÓRICO
    # ==================================================

    def save_history(
        self,
        data
    ):

        """
        Guarda snapshots para treinamento futuro.
        """

        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d_%H%M%S"
            )
        )


        filename = (
            f"history_{timestamp}.json"
        )


        filepath = (
            self.history_path /
            filename
        )


        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


        return filepath



    # ==================================================
    # CONVERSÃO PARA IA
    # ==================================================

    def prepare_for_ai(
        self,
        data
    ):

        """
        Converte dados para dataframe
        utilizado pelos modelos.
        """


        if not data:
            return pd.DataFrame()



        rows = []


        for event in data:


            rows.append({

                "home_team":
                    event["home_team"],

                "away_team":
                    event["away_team"],

                "sport":
                    event["sport"],

                "league":
                    event["league"],

            })


        df = pd.DataFrame(rows)


        return df



    # ==================================================
    # PIPELINE COMPLETO
    # ==================================================

    def process_pipeline(
        self,
        raw_data
    ):

        """
        Executa todo fluxo:

        API
        ↓
        limpeza
        ↓
        padronização
        ↓
        armazenamento
        ↓
        IA
        """


        self.save_raw_data(
            raw_data
        )


        clean = self.clean_data(
            raw_data
        )


        self.save_clean_data(
            clean
        )


        self.save_history(
            clean
        )


        ai_dataset = (
            self.prepare_for_ai(
                clean
            )
        )


        return ai_dataset
