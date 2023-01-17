"""Return types of the HelpDesk / LiveChat API

Documentation: https://api.helpdesk.com/docs

ToDo:
    * Implement the types below correctly instead of using `Extra.Allow`
    * Find out why `extra=Extra.allow` causes mypy to fail. Seems like a bug in pydantic.
"""
from typing import List, Optional

from pydantic import BaseModel, Extra


class Id(BaseModel):
    ID: str


class Agent(BaseModel, extra=Extra.allow):  # type: ignore
    pass


class Team(BaseModel, extra=Extra.allow):  # type: ignore
    pass


class Message(BaseModel, extra=Extra.allow):  # type: ignore
    text: str


class Requester(BaseModel):
    email: str
    name: str


class Assignment(BaseModel, extra=Extra.allow):  # type: ignore
    team: Id
    agent: Id


class NewTicket(BaseModel, extra=Extra.allow):  # type: ignore
    """Object that needs to be sent when creating a NEW ticket"""

    message: Message
    requester: Requester
    status: Optional[str]  # ToDo: Rather use an Enum instead
    subject: Optional[str]
    teamIDs: Optional[List[str]]
    assignment: Optional[Assignment]


class Ticket(BaseModel, extra=Extra.allow):  # type: ignore
    """Actual ticket as returned by the API"""
