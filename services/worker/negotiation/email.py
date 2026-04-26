"""Email communication system for negotiations."""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailClient:
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: str = "AAN Buyer",
    ) -> bool:
        if not to or not body:
            return False

        msg = MIMEMultipart()
        msg["From"] = f"{from_name} <{self.username}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg["Message-ID"] = f"<{datetime.utcnow().timestamp()}@aan.negotiator>"

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            server.quit()

            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    def send_negotiation_message(
        self,
        to: str,
        product: str,
        message: str,
    ) -> bool:
        subject = f"Re: {product} - Buyer Inquiry"
        return self.send_email(to, subject, message)

    def send_counter_offer(
        self,
        to: str,
        product: str,
        offer: float,
        message: str,
    ) -> bool:
        subject = f"Re: {product} - Offer of AED {offer}"
        return self.send_email(to, subject, message)

    def send_acceptance(
        self,
        to: str,
        product: str,
        agreed_price: float,
    ) -> bool:
        subject = f"{product} - I'll take it at AED {agreed_price}"
        body = f"Hi,\n\nI'm happy to accept your offer of AED {agreed_price}. When can I come pick it up?\n\nThanks!"
        return self.send_email(to, subject, body)


class IMAPClient:
    def __init__(
        self,
        imap_host: str = "imap.gmail.com",
        username: str = "",
        password: str = "",
    ):
        self.imap_host = imap_host
        self.username = username
        self.password = password

    def check_for_replies(
        self,
        from_address: str,
        since: Optional[datetime] = None,
    ) -> list[dict]:
        import imaplib
        import email

        replies = []

        try:
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.username, self.password)
            mail.select("INBOX")

            search_criteria = f'FROM "{from_address}"'
            if since:
                since_str = since.strftime("%d-%b-%Y")
                search_criteria += f' SINCE {since_str}'

            typ, data = mail.search(None, search_criteria)

            for num in data[0].split():
                typ, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg_content = response_part[1]
                        msg = email.message_from_bytes(msg_content)

                        subject = msg.get("Subject", "")
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        replies.append({
                            "subject": subject,
                            "body": body,
                            "from": from_address,
                        })

            mail.close()
            mail.logout()

        except Exception as e:
            logger.error(f"Failed to check for replies: {e}")

        return replies


async def send_negotiation_email(
    to: str,
    subject: str,
    message: str,
) -> bool:
    from config.core.settings import get_settings

    settings = get_settings()

    client = EmailClient(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
    )

    return client.send_email(to, subject, message)