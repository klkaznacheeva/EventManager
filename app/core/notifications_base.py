# app/core/notifications_base.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class NotificationProvider(ABC):

    @abstractmethod
    async def send(self, to: str, subject: str, message: str, data: Dict[str, Any] = None):
        pass