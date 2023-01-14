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


class Recipient(BaseModel, extra=Extra.allow):  # type: ignore
    """Details about the recipient

    We allow extra fields that can be used for customization
    """

    name: str
    email: str
    address_as: Optional[str]  # could be the first name

    @validator("address_as")
    @classmethod
    def fill_with_name(cls, v, values):
        if v is None:
            v = values["name"]
        return v


class Mail(BaseModel, extra=Extra.allow):  # type: ignore
    """Mail template

    We allow extra fields that can be used for customization.

    You can use the typical [Format String Syntax] and the objects `recipient` and `mail`
    to access metadata to complement the template, e.g.:

    ```
    Hello {recipient.address_as},

    We hope it's ok to address you your first name rather than using your full name being {recipient.name}.
    Have you read the email's subject '{mail.subject}'?

    Cheers!
    ```

    [Format String Syntax]: https://docs.python.org/3/library/string.html#formatstrings
    """

    subject: str
    team_id: str
    agent_id: str
    text: str
    status: str = "solved"  # ToDo: Reconsider this!
    recipients: list[Recipient]


class MailClient:
    def __init__(self, helpdesk_api: HelpDeskAPI):
        self._helpdesk_api = helpdesk_api
        self.mail: Optional[Mail] = None

    def set_mail(self, mail: Mail) -> "MailClient":
        self.mail = mail
        return self

    def _create_ticket(self, mail_text: str, recipient: Recipient) -> NewTicket:
        if self.mail is None:
            raise RuntimeError("There is no mail to create a ticket from!")
        message = Message(text=mail_text)
        requester = Requester(name=recipient.name, email=recipient.email)
        team_id, agent_id = Id(ID=self.mail.team_id), Id(ID=self.mail.agent_id)
        assignment = Assignment(team=team_id, agent=agent_id)
        ticket = NewTicket(
            requester=requester,
            message=message,
            subject=self.mail.subject,
            assignment=assignment,
            status=self.mail.status,
            teamIDs=[self.mail.team_id],
        )
        return ticket

    def sent(self) -> tuple[List[Tuple[Recipient, Ticket]], List[Tuple[Recipient, Exception]]]:
        if self.mail is None:
            raise RuntimeError("There is no mail to be sent!")

        errors = []
        tickets = []
        for recipient in self.mail.recipients:
            try:
                mail_text = self.mail.text.format(recipient=recipient, mail=self.mail)
                ticket = self._create_ticket(mail_text, recipient)
                resp = self._helpdesk_api.create_ticket(ticket)
                resp_ticket = Ticket.parse_obj(resp)
            except Exception as e:
                errors.append((recipient, e))
            else:
                tickets.append((recipient, resp_ticket))
        return tickets, errors
