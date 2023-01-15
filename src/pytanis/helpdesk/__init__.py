"""Functionality around the HelpDesk / LiveChat API"""

from .api import HelpDeskAPI
from .mail import Mail, MailClient, Recipient

__all__ = ["HelpDeskAPI", "Mail", "MailClient", "Recipient"]
