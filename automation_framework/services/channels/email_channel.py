"""
Email channel adapter via Proton Bridge (IMAP/SMTP).

Proton Bridge exposes standard IMAP (port 1143) and SMTP (port 1025)
on localhost. This adapter uses stdlib imaplib/smtplib with STARTTLS.

Polling uses IMAP SEARCH for UNSEEN messages. After processing, messages
are flagged as SEEN so they aren't re-processed on the next poll.
"""

import email
import email.utils
import imaplib
import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from .base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    OutboundMessage,
)
from ..config import EmailConfig

logger = logging.getLogger(__name__)


class EmailChannel(BaseChannel):
    """Email adapter using Proton Bridge IMAP/SMTP."""

    channel_type = ChannelType.EMAIL

    def __init__(self, config: EmailConfig):
        self.config = config
        self._imap: Optional[imaplib.IMAP4] = None

    def _connect_imap(self) -> imaplib.IMAP4:
        """Connect to Proton Bridge IMAP."""
        if self._imap is not None:
            try:
                self._imap.noop()
                return self._imap
            except Exception:
                self._imap = None

        logger.debug(
            "Connecting to IMAP %s:%d",
            self.config.imap_host, self.config.imap_port
        )

        ctx = ssl.create_default_context()
        # Proton Bridge uses a self-signed cert on localhost
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        imap = imaplib.IMAP4(self.config.imap_host, self.config.imap_port, timeout=10)
        imap.starttls(ssl_context=ctx)
        imap.login(self.config.username, self.config.password)
        self._imap = imap
        return imap

    def _disconnect_imap(self) -> None:
        """Cleanly close the IMAP connection."""
        if self._imap is not None:
            try:
                self._imap.close()
                self._imap.logout()
            except Exception:
                pass
            self._imap = None

    def poll(self) -> list[InboundMessage]:
        """Check for new unseen messages in watched folders."""
        messages = []
        try:
            imap = self._connect_imap()
        except Exception as e:
            logger.error("IMAP connection failed: %s", e)
            return messages

        for folder in self.config.watch_folders:
            try:
                status, _ = imap.select(folder)
                if status != "OK":
                    logger.warning("Could not select folder: %s", folder)
                    continue

                # Search for unseen messages
                status, data = imap.search(None, "UNSEEN")
                if status != "OK" or not data[0]:
                    continue

                msg_nums = data[0].split()
                logger.info(
                    "Found %d unseen messages in %s", len(msg_nums), folder
                )

                for num in msg_nums:
                    try:
                        msg = self._fetch_message(imap, num)
                        if msg is not None:
                            messages.append(msg)
                    except Exception as e:
                        logger.error(
                            "Error fetching message %s: %s", num, e
                        )

            except Exception as e:
                logger.error("Error polling folder %s: %s", folder, e)

        return messages

    def _fetch_message(
        self, imap: imaplib.IMAP4, msg_num: bytes
    ) -> Optional[InboundMessage]:
        """Fetch and parse a single email message."""
        status, data = imap.fetch(msg_num, "(RFC822)")
        if status != "OK" or not data[0]:
            return None

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract body (prefer plain text)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="replace")
                    break
            # Fallback to HTML if no plain text
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="replace")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="replace")

        # Parse timestamp
        date_str = msg.get("Date", "")
        try:
            parsed_date = email.utils.parsedate_to_datetime(date_str)
        except Exception:
            parsed_date = datetime.now()

        # Extract sender
        from_header = msg.get("From", "")
        sender_name, sender_addr = email.utils.parseaddr(from_header)
        sender = sender_addr or from_header

        # Message-ID for deduplication
        message_id = msg.get("Message-ID", f"imap-{msg_num.decode()}")

        # References/In-Reply-To for threading
        reply_to = msg.get("In-Reply-To", "")
        references = msg.get("References", "")
        thread_id = references.split()[0] if references else reply_to

        return InboundMessage(
            channel=ChannelType.EMAIL,
            sender=sender,
            subject=msg.get("Subject", "(no subject)"),
            body=body,
            timestamp=parsed_date,
            message_id=message_id,
            reply_to=reply_to or None,
            thread_id=thread_id or None,
            raw={"from_name": sender_name, "to": msg.get("To", "")},
        )

    def send(self, message: OutboundMessage) -> bool:
        """Send an email via Proton Bridge SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.config.sender_address
            msg["To"] = message.recipient
            msg["Subject"] = message.subject

            if message.reply_to:
                msg["In-Reply-To"] = message.reply_to
                msg["References"] = message.reply_to

            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(
                self.config.smtp_host, self.config.smtp_port
            ) as smtp:
                smtp.starttls(context=ctx)
                smtp.login(self.config.username, self.config.password)
                smtp.send_message(msg)

            logger.info(
                "Email sent to %s: %s", message.recipient, message.subject
            )
            return True

        except Exception as e:
            logger.error("Failed to send email to %s: %s", message.recipient, e)
            return False

    def save_draft(self, message: OutboundMessage) -> bool:
        """
        Save a draft reply into the Proton Bridge Drafts folder via IMAP APPEND.

        The draft appears in the Proton client (desktop/mobile) ready for
        review, editing, and manual sending. Uses the \\Draft flag so the
        mail client treats it as an unsent draft.
        """
        try:
            imap = self._connect_imap()

            msg = MIMEMultipart("alternative")
            msg["From"] = self.config.sender_address
            msg["To"] = message.recipient
            msg["Subject"] = message.subject
            msg["Date"] = email.utils.formatdate(localtime=True)
            msg["X-SEBE-Draft"] = "true"

            if message.reply_to:
                msg["In-Reply-To"] = message.reply_to
                msg["References"] = message.reply_to

            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            raw_msg = msg.as_bytes()
            status, _ = imap.append(
                "Drafts",
                "\\Draft \\Seen",
                imaplib.Time2Internaldate(datetime.now().astimezone()),
                raw_msg,
            )

            if status == "OK":
                logger.info(
                    "Draft saved for %s: %s",
                    message.recipient, message.subject,
                )
                return True
            else:
                logger.error(
                    "IMAP APPEND to Drafts failed (status=%s)", status
                )
                return False

        except Exception as e:
            logger.error("Failed to save draft for %s: %s", message.recipient, e)
            return False

    def is_available(self) -> bool:
        """Check if Proton Bridge IMAP is reachable."""
        try:
            imap = self._connect_imap()
            imap.noop()
            return True
        except Exception:
            return False
