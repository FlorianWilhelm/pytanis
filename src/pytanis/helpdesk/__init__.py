"""Functionality around the HelpDesk / LiveChat API"""

from .client import HelpDeskClient
from .mail import Mail, MailClient, Recipient

__all__ = ["HelpDeskClient", "Mail", "MailClient", "Recipient"]
