# app/services/notification_service.py
from app.core.notifications.email_renderer import render_email_template
from app.core.notifications.providers.factory import NotificationFactory


class NotificationService:

    @staticmethod
    async def send_email(
            to: str,
            subject: str,
            template_name: str,
            context: dict
    ):
        provider = NotificationFactory.get_provider()

        html = render_email_template(
            template_name,
            context
        )

        await provider.send(
            to=to,
            subject=subject,
            message=html
        )