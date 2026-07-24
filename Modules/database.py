"""
OddReal 2.0
Gerenciador de Banco de Dados
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, List, Optional

from modules.logger import info, error


DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "oddreal.db"


class DatabaseManager:

    def __init__(self):

        self.connection = sqlite3.connect(
            DATABASE_FILE,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        info("Banco de dados conectado.")

    def execute(
        self,
        query: str,
        params: tuple = ()
    ) -> None:

        try:

            cursor = self.connection.cursor()

            cursor.execute(query, params)

            self.connection.commit()

        except Exception as e:

            error(f"Erro SQL: {e}")

            raise

    def fetchone(
        self,
        query: str,
        params: tuple = ()
    ) -> Optional[sqlite3.Row]:

        cursor = self.connection.cursor()

        cursor.execute(query, params)

        return cursor.fetchone()

    def fetchall(
        self,
        query: str,
        params: tuple = ()
    ) -> List[sqlite3.Row]:

        cursor = self.connection.cursor()

        cursor.execute(query, params)

        return cursor.fetchall()

    def close(self):

        self.connection.close()

        info("Banco de dados encerrado.")


db = DatabaseManager()
