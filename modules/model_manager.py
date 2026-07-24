"""
OddReal 2.0
Gerenciador de Modelos
"""

from __future__ import annotations

from typing import Any, Dict

from modules.logger import info, warning


class ModelManager:
    """
    Gerencia todos os modelos utilizados
    pelo OddReal.
    """

    def __init__(self):

        self.models: Dict[str, Any] = {}

        info("Model Manager iniciado.")

    def register(
        self,
        name: str,
        model: Any
    ) -> None:

        self.models[name] = model

        info(f"Modelo '{name}' registrado.")

    def get(
        self,
        name: str
    ) -> Any:

        model = self.models.get(name)

        if model is None:

            warning(
                f"Modelo '{name}' não encontrado."
            )

        return model

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self.models

    def remove(
        self,
        name: str
    ) -> None:

        if name in self.models:

            del self.models[name]

            info(
                f"Modelo '{name}' removido."
            )

    def list_models(self):

        return list(self.models.keys())

    def total_models(self) -> int:

        return len(self.models)

    def clear(self):

        self.models.clear()

        info("Todos os modelos removidos.")


model_manager = ModelManager()
