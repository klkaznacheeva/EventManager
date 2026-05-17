from app.core.config import settings

from app.core.notifications.providers.mailtrap_provider import (
    MailtrapProvider
)
from app.core.notifications.providers.unisender_provider import UniSenderProvider


class NotificationFactory:
    @staticmethod
    def get_provider():
        if settings.MAIL_PROVIDER == "mailtrap":
            return MailtrapProvider()
        if settings.MAIL_PROVIDER == "unisender":
            return UniSenderProvider()   # создадим его ниже
        raise Exception("Notification provider not configured")