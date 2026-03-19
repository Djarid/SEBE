"""
Email channel adapter via Proton Bridge (IMAP/SMTP).

Proton Bridge exposes standard IMAP (port 1143) and SMTP (port 1025)
on localhost. This adapter uses stdlib imaplib/smtplib with STARTTLS.

Polling uses IMAP SEARCH for UNSEEN messages. After processing, messages
are flagged as SEEN so they aren't re-processed on the next poll.
"""

import email
import email.utils
import html.parser
import imaplib
import logging
import mimetypes
import re
import smtplib
import ssl
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from .base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    OutboundMessage,
)
from ..config import EmailConfig
from tools.url_sanitise import defang_url, defang_urls

logger = logging.getLogger(__name__)


class _HTMLTextExtractor(html.parser.HTMLParser):
    """Stdlib HTML-to-text converter for email bodies.

    Preserves hyperlink URLs by appending the href after the link text
    in defanged form:  ``Link text (hxxps://example[.]com/path)``

    URLs are defanged at extraction time as a defence-in-depth measure
    to prevent accidental navigation via browser automation tools.
    """

    _BLOCK_TAGS = frozenset(
        (
            "br",
            "p",
            "div",
            "tr",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "blockquote",
            "pre",
            "hr",
            "table",
            "thead",
            "tbody",
        )
    )
    _SKIP_TAGS = frozenset(("style", "script", "head"))

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth: int = 0
        # Stack of (href, text_start_index) for nested <a> tags
        self._link_stack: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        if tag in self._BLOCK_TAGS:
            self._parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href", "")
            self._link_stack.append((href, len(self._parts)))

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        if tag in self._BLOCK_TAGS:
            self._parts.append("\n")
        if tag == "a" and self._link_stack:
            href, text_start = self._link_stack.pop()
            if href and re.match(r"https?://", href, re.IGNORECASE):
                # Extract the visible link text accumulated since <a>
                link_text = "".join(self._parts[text_start:]).strip()
                # Avoid redundant output when link text IS the URL
                if link_text.rstrip("/") != href.rstrip("/"):
                    self._parts.append(f" ({defang_url(href)})")
                else:
                    # Replace the bare URL text with defanged version
                    self._parts[text_start:] = [defang_url(href)]

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def _html_to_text(html_str: str) -> str:
    """Convert HTML email body to readable plain text. Stdlib only.

    URLs are defanged in two passes:
    1. <a> href URLs are defanged by _HTMLTextExtractor during parsing.
    2. Any remaining bare URLs in the text output are caught here.
    """
    parser = _HTMLTextExtractor()
    parser.feed(html_str)
    return defang_urls(parser.get_text())


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
            "Connecting to IMAP %s:%d", self.config.imap_host, self.config.imap_port
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
                logger.info("Found %d unseen messages in %s", len(msg_nums), folder)

                for num in msg_nums:
                    try:
                        msg = self._fetch_message(imap, num)
                        if msg is not None:
                            messages.append(msg)
                    except Exception as e:
                        logger.error("Error fetching message %s: %s", num, e)

            except Exception as e:
                logger.error("Error polling folder %s: %s", folder, e)

        return messages

    def search_by_date(
        self,
        folder: str,
        since_date: str,
        mark_seen: bool = False,
    ) -> list[InboundMessage]:
        """Search a folder for all messages since a date (YYYY-MM-DD).

        Unlike poll(), this searches by date (not UNSEEN) and opens the
        folder in readonly mode by default so message flags are untouched.
        """
        messages = []
        try:
            imap = self._connect_imap()
        except Exception as e:
            logger.error("IMAP connection failed: %s", e)
            return messages

        try:
            status, _ = imap.select(folder, readonly=not mark_seen)
            if status != "OK":
                logger.warning("Could not select folder: %s", folder)
                return messages

            # IMAP SINCE uses DD-Mon-YYYY format
            dt = datetime.strptime(since_date, "%Y-%m-%d")
            imap_date = dt.strftime("%d-%b-%Y")

            status, data = imap.search(None, f"SINCE {imap_date}")
            if status != "OK" or not data[0]:
                return messages

            msg_nums = data[0].split()
            logger.info(
                "Found %d messages in %s since %s", len(msg_nums), folder, since_date
            )

            for num in msg_nums:
                try:
                    msg = self._fetch_message(imap, num)
                    if msg is not None:
                        messages.append(msg)
                except Exception as e:
                    logger.error("Error fetching message %s: %s", num, e)

        except Exception as e:
            logger.error("Error searching folder %s: %s", folder, e)

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

        # Extract body (prefer plain text).
        # All URLs are defanged regardless of content type to prevent
        # accidental navigation via browser automation tools.
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = defang_urls(payload.decode("utf-8", errors="replace"))
                    break
            # Fallback to HTML if no plain text
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = _html_to_text(
                                payload.decode("utf-8", errors="replace")
                            )
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="replace")
                if msg.get_content_type() == "text/html":
                    body = _html_to_text(body)
                else:
                    body = defang_urls(body)

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
            raw={
                "from_name": sender_name,
                "to": msg.get("To", ""),
                "cc": msg.get("Cc", ""),
            },
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

            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as smtp:
                smtp.starttls(context=ctx)
                smtp.login(self.config.username, self.config.password)
                smtp.send_message(msg)

            logger.info("Email sent to %s: %s", message.recipient, message.subject)
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
                    message.recipient,
                    message.subject,
                )
                return True
            else:
                logger.error("IMAP APPEND to Drafts failed (status=%s)", status)
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
