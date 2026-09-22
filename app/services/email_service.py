import logging
import smtplib
from email.message import EmailMessage
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    # Keeps track of the last verification email sent (convenient for local dev & automated testing)
    last_sent_email = None

    @classmethod
    def send_verification_email(cls, recipient_email: str, raw_token: str) -> bool:
        verification_link = f"{settings.app_base_url}/verify?token={raw_token}"
        cls.last_sent_email = {
            "recipient": recipient_email,
            "token": raw_token,
            "link": verification_link,
        }

        msg = EmailMessage()
        msg["Subject"] = "Verify Your Spend Tracker Account"
        msg["From"] = settings.smtp_from_email
        msg["To"] = recipient_email

        body_text = (
            f"Hello,\n\n"
            f"Thank you for signing up for Spend Tracker!\n\n"
            f"Please verify your email address by clicking the link below:\n"
            f"{verification_link}\n\n"
            f"This link is valid for {settings.email_verification_token_expire_hours} hours and can only be used once.\n\n"
            f"If you did not sign up for this account, please disregard this email.\n"
        )
        msg.set_content(body_text)

        body_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #faf8ff; margin: 0; padding: 24px; color: #131b2e; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border: 1px solid #dae2fd; border-radius: 16px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .logo {{ display: inline-block; background-color: #005c55; color: #ffffff; padding: 8px 14px; border-radius: 8px; font-weight: bold; font-size: 16px; margin-bottom: 20px; letter-spacing: -0.5px; }}
    h1 {{ font-size: 22px; color: #131b2e; margin-top: 0; font-weight: 700; }}
    p {{ font-size: 15px; line-height: 1.6; color: #3e4947; margin: 12px 0; }}
    .btn-container {{ text-align: center; margin: 28px 0; }}
    .btn {{ display: inline-block; background-color: #005c55; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 10px; font-weight: 600; font-size: 15px; box-shadow: 0 2px 6px rgba(0,92,85,0.25); }}
    .link-alt {{ font-size: 12px; word-break: break-all; color: #006a61; }}
    .footer {{ margin-top: 24px; font-size: 12px; color: #6e7977; border-top: 1px solid #eaedff; padding-top: 16px; line-height: 1.5; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">SpendTrack</div>
    <h1>Verify Your Email Address</h1>
    <p>Hello,</p>
    <p>Thank you for signing up for SpendTrack! To activate your account and start managing your expenses, please click the button below to verify your email:</p>
    <div class="btn-container">
      <a href="{verification_link}" class="btn" target="_blank">Verify Email Address</a>
    </div>
    <p>This verification link is valid for <strong>{settings.email_verification_token_expire_hours} hours</strong> and can only be used once.</p>
    <div class="footer">
      If the button above does not work, copy and paste this link into your browser:<br>
      <a href="{verification_link}" class="link-alt">{verification_link}</a><br><br>
      If you did not create a SpendTrack account, you can safely ignore this email.
    </div>
  </div>
</body>
</html>"""
        msg.add_alternative(body_html, subtype="html")

        # Attempt sending email via configured SMTP
        try:
            if settings.app_env in ("test", "testing") or settings.smtp_host in ("smtp.example.com", "example.com"):
                logger.info("Mock SMTP mode active (%s). Verification link: %s", settings.smtp_host, verification_link)
                return True

            logger.info("Attempting to send verification email to %s via %s:%s", recipient_email, settings.smtp_host, settings.smtp_port)
            if settings.smtp_use_tls:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5) as server:
                    server.starttls()
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5) as server:
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg)
            logger.info("Verification email successfully sent to %s", recipient_email)
            return True
        except Exception as e:
            # In dev/test or when SMTP server is unreachable, log warning without breaking user signup
            logger.warning("SMTP email sending failed to %s: %s. Link: %s", recipient_email, e, verification_link)
            return False


email_service = EmailService()
