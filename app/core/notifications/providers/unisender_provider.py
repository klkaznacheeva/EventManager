from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.notifications_base import NotificationProvider
from app.core.config import settings

class UniSenderProvider(NotificationProvider):
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_HOST,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

    async def send(self, to: str, subject: str, message: str, data=None):
        html = message
        email = MessageSchema(
            subject=subject,
            recipients=[to],
            body=html,
            subtype="html"
        )
        fm = FastMail(self.conf)
        await fm.send_message(email)