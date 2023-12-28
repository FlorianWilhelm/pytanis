"""Return types of the HelpDesk / LiveChat API

Documentation: https://api.helpdesk.com/docs

ToDo:
    * Implement the types below correctly instead of using `Extra.Allow`
    * Find out why `extra=Extra.allow` causes mypy to fail. Seems like a bug in pydantic.
"""

from pydantic import BaseModel


class Id(BaseModel):
    ID: str


class Agent(BaseModel, extra='allow'):
    pass


class Team(BaseModel, extra='allow'):
    pass


class Message(BaseModel, extra='allow'):
    text: str


class Requester(BaseModel):
    email: str
    name: str


class Assignment(BaseModel, extra='allow'):
    team: Id
    agent: Id


class NewTicket(BaseModel, extra='allow'):
    """Object that needs to be sent when creating a NEW ticket"""

    message: Message
    requester: Requester
    status: str | None = None  # ToDo: Rather use an Enum instead
    subject: str | None = None
    teamIDs: list[str] | None = None  # noqa: N815
    assignment: Assignment | None = None


class Ticket(BaseModel, extra='allow'):
    """Actual ticket as returned by the API"""
