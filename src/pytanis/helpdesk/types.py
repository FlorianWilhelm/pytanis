"""Return types of the HelpDesk / LiveChat API

Documentation: https://api.helpdesk.com/docs

ToDo:
    * Implement the types below correctly instead of using `Extra.Allow`
"""
from typing import List, Optional

from pydantic import BaseModel, Extra


class Id(BaseModel):
    ID: str


class Agent(BaseModel, extra=Extra.allow):
    pass


class Team(BaseModel, extra=Extra.allow):
    pass


class Message(BaseModel, extra=Extra.allow):
    text: str


class Requester(BaseModel):
    email: str
    name: str


class Assignment(BaseModel, extra=Extra.allow):
    team: Id
    agent: Id


class NewTicket(BaseModel, extra=Extra.allow):
    """Object that needs to be sent when creating a NEW ticket"""

    message: Message
    requester: Requester
    status: Optional[str]  # ToDo: Rather use an Enum instead
    subject: Optional[str]
    teamIDs: Optional[List[str]]
    assignment: Optional[Assignment]


class Ticket(BaseModel, extra=Extra.allow):
    """Actual ticket as returned by the API"""

    pass
