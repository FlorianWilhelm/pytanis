"""Functionality around the HelpDesk / LiveChat API"""

from pytanis.helpdesk.client import HelpDeskClient
from pytanis.helpdesk.mail import Mail, MailClient, Recipient

__all__ = ['HelpDeskClient', 'Mail', 'MailClient', 'Recipient']
