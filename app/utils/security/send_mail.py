import smtplib
import asyncio
from email.message import EmailMessage
from app.config import settings

async def send_mail(send_to: str, subject: str, message: str):
    def _send():
        msg = EmailMessage()
        msg["From"] = settings.smtp_user
        msg["To"] = send_to
        msg["Subject"] = subject
        msg.set_content(message)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as connection:
            connection.starttls()
            connection.login(settings.smtp_user, settings.smtp_password)
            connection.send_message(msg)

    await asyncio.to_thread(_send)
