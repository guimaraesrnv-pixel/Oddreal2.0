"""
OddReal 2.0
Módulo de Log Centralizado

Responsável por registrar eventos, erros, avisos e informações do sistema.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "oddreal.log"


class LoggerManager:
    """
    Gerencia o logger principal do OddReal.
    """

    _logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:

        if cls._logger is not None:
            return cls._logger

        logger = logging.getLogger("OddReal")

        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
            "%d/%m/%Y %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._logger = logger

        return logger


logger = LoggerManager.get_logger()


def info(message: str):

    logger.info(message)


def warning(message: str):

    logger.warning(message)


def error(message: str):

    logger.error(message)


def critical(message: str):

    logger.critical(message)


def exception(message: str):

    logger.exception(message)


def debug(message: str):

    logger.debug(message)
