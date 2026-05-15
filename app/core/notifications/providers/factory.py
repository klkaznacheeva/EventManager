from app.core.config import settings

from app.core.notifications.providers.mailtrap_provider import (
    MailtrapProvider
)


class NotificationFactory:

    @staticmethod
    def get_provider():

        if settings.MAIL_PROVIDER == "mailtrap":
            return MailtrapProvider()

        raise Exception("Notification provider not configured")