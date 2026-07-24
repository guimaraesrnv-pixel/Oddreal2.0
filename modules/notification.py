"""
OddReal 2.0
Sistema de Notificações
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from modules.logger import info


class NotificationManager:
    """
    Gerencia todas as notificações
    do OddReal.
    """

    def __init__(self):

        self.notifications: List[Dict] = []

        info("Notification Manager iniciado.")

    def add(
        self,
        title: str,
        message: str,
        level: str = "info"
    ) -> None:

        self.notifications.append({

            "title": title,

            "message": message,

            "level": level,

            "created_at": datetime.now()

        })

    def all(self) -> List[Dict]:

        return self.notifications

    def unread(self) -> List[Dict]:

        return [

            notification

            for notification in self.notifications

            if not notification.get(
                "read",
                False
            )

        ]

    def mark_as_read(
        self,
        index: int
    ) -> None:

        if 0 <= index < len(self.notifications):

            self.notifications[index]["read"] = True

    def clear(self) -> None:

        self.notifications.clear()

    def total(self) -> int:

        return len(self.notifications)


notification_manager = NotificationManager()
