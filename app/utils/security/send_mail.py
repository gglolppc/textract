import smtplib
import asyncio
from email.message import EmailMessage
from app.config.config import settings


async def send_mail(send_to: str, subject: str, message: str):
    """
    Sends a stylish HTML email (OTP / verification / notification)
    """
    def _send():
        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = send_to
        msg["Subject"] = subject

        # Plain text fallback
        msg.set_content(f"Your verification code: {message}")

        # HTML version
        html = f"""
        <html>
          <body style="margin:0; padding:0; background-color:#0f0f10; font-family:'Poppins','Segoe UI',Arial,sans-serif;">
            <div style="height:80px;"></div> <!-- Верхний отступ -->

            <table align="center" cellpadding="0" cellspacing="0" width="100%" style="max-width:480px; margin:auto; background-color:#1a1a1c; border-radius:16px; box-shadow:0 4px 16px rgba(0,0,0,0.25); overflow:hidden;">
              <tr>
                <td style="background:linear-gradient(90deg,#7e22ce,#9333ea); padding:24px; text-align:center;">
                  <h1 style="color:#fff; margin:0; font-size:24px; font-weight:600; letter-spacing:1px;">textract.me</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:40px 30px; text-align:center; color:#f0f0f0;">
                  <h2 style="color:#a855f7; margin:0 0 10px; font-size:20px;">Your Verification Code</h2>
                  <p style="font-size:15px; line-height:1.6; color:#ccc; margin:0 0 28px;">
                    Use the code below to verify your email address<br>or complete your login:
                  </p>
                  <div style="display:inline-block; background-color:#ffffff; color:#111; font-size:36px; font-weight:700; letter-spacing:6px; padding:16px 28px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.25);">
                    {message}
                  </div>
                  <p style="margin-top:32px; font-size:13px; color:#888; line-height:1.6;">
                    This code will expire in 10 minutes.<br>
                    If you didn’t request this code, you can safely ignore this email.
                  </p>
                </td>
              </tr>

              <tr>
                <td style="text-align:center; background-color:#111; padding:16px; color:#555; font-size:12px;">
                  © 2025 <span style="color:#a855f7;">textract.me</span> — powered by AI
                </td>
              </tr>
            </table>

            <div style="height:60px;"></div> <!-- Нижний отступ -->
          </body>
        </html>
        """

        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as connection:
            connection.starttls()
            connection.login(settings.smtp_user, settings.smtp_password)
            connection.send_message(msg)

    await asyncio.to_thread(_send)
