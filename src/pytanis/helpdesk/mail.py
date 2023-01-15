"""Functionality around mailing

ToDo:
    * add logging where appropriate
    * Find out why `extra=Extra.allow` causes mypy to fail. Seems like a bug in pydantic.
"""
from typing import List, Optional, Tuple

from pydantic import BaseModel, Extra, validator
from structlog import get_logger

from .api import HelpDeskAPI
from .types import Assignment, Id, Message, NewTicket, Requester, Ticket

logger = get_logger()


class MetaData(BaseModel, extra=Extra.allow):  # type: ignore
    """Additional, arbitrary metadata provided by the user like for template filling"""


class Recipient(BaseModel):
    """Details about the recipient

    Use the `data` field to store additional information
    """

    name: str
    email: str
    address_as: Optional[str]  # could be the first name
    data: MetaData

    @validator("address_as")
    @classmethod
    def fill_with_name(cls, v, values):
        if v is None:
            v = values["name"]
        return v


class Mail(BaseModel):
    """Mail template

    Use the `data` field to store additional information

    You can use the typical [Format String Syntax] and the objects `recipient` and `mail`
    to access metadata to complement the template, e.g.:

    ```
    Hello {recipient.address_as},

    We hope it's ok to address you your first name rather than using your full name being {recipient.name}.
    Have you read the email's subject '{mail.subject}'? How is your work right now at {recipient.data.company}?

    Cheers!
    ```

    [Format String Syntax]: https://docs.python.org/3/library/string.html#formatstrings
    """

    subject: str
    team_id: str
    agent_id: str
    text: str
    status: str = "solved"  # ToDo: Reconsider this!
    recipients: List[Recipient]
    data: MetaData


class MailClient:
    def __init__(self, helpdesk_api: HelpDeskAPI):
        self._helpdesk_api = helpdesk_api

    @staticmethod
    def _create_ticket(mail: Mail, mail_text: str, recipient: Recipient) -> NewTicket:
        message = Message(text=mail_text)
        requester = Requester(name=recipient.name, email=recipient.email)
        team_id, agent_id = Id(ID=mail.team_id), Id(ID=mail.agent_id)
        assignment = Assignment(team=team_id, agent=agent_id)
        ticket = NewTicket(
            requester=requester,
            message=message,
            subject=mail.subject,
            assignment=assignment,
            status=mail.status,
            teamIDs=[mail.team_id],
        )
        return ticket

    def sent(self, mail: Mail) -> Tuple[List[Tuple[Recipient, Ticket]], List[Tuple[Recipient, Exception]]]:
        errors = []
        tickets = []
        for recipient in mail.recipients:
            try:
                mail_text = mail.text.format(recipient=recipient, mail=mail)
                ticket = self._create_ticket(mail, mail_text, recipient)
                resp = self._helpdesk_api.create_ticket(ticket)
                resp_ticket = Ticket.parse_obj(resp)
            except Exception as e:
                errors.append((recipient, e))
            else:
                tickets.append((recipient, resp_ticket))
        return tickets, errors
