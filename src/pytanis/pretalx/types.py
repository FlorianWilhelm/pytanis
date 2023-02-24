"""Return types of the Pretalx API

Documentation: https://docs.pretalx.org/api/resources/index.html

Attention: Quite often the API docs and the actual results of the API differ!

ToDo:
    * Find out why `extra=Extra.allow` causes mypy to fail. Seems like a bug in pydantic.
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field


class Me(BaseModel):
    name: str
    email: str
    local: Optional[str]
    timezone: str


class MultiLingualStr(BaseModel, extra=Extra.allow):  # type: ignore
    # ToDo: Add here more available languages, not mentioned in the API
    en: Optional[str]  # we assume though that english is always given to simplify things
    de: Optional[str]


class URLs(BaseModel):
    base: str
    schedule: str
    login: str
    feed: str


class Event(BaseModel):
    name: MultiLingualStr
    slug: str
    is_public: bool
    date_from: date
    date_to: Optional[date]
    timezone: str
    urls: URLs


class SpeakerAvailability(BaseModel):
    # ToDo: Check the datatypes here again, not mentioned in the API
    id: int
    start: str
    end: str
    allDay: str = Field(..., alias="all_day")


class AnswerQuestionRef(BaseModel):
    id: int
    question: MultiLingualStr


class Option(BaseModel):
    id: int
    answer: MultiLingualStr


class Answer(BaseModel):
    id: int
    answer: str
    answer_file: Optional[str]
    question: AnswerQuestionRef
    submission: Optional[str]
    review: Optional[int]
    person: Optional[str]
    options: List[Option]


class SubmissionSpeaker(BaseModel):
    code: str
    name: str
    biography: Optional[str]
    avatar: Optional[str]
    email: Optional[str]


class Speaker(SubmissionSpeaker):
    submissions: List[str]  # submission codes
    availabilities: Optional[List[SpeakerAvailability]]  # maybe needs organizer permissions?
    answers: Optional[List[Answer]]  # maybe needs organizer permissions?


class Slot(BaseModel):
    # ToDo: Check the datatypes here again, not mentioned in the API
    start: str
    end: str
    room: MultiLingualStr
    room_id: int


class Resource(BaseModel):
    resource: str
    description: str


class State(Enum):
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"  # is "Not accepted" in WebUI
    confirmed = "confirmed"
    withdrawn = "withdrawn"
    canceled = "canceled"
    deleted = "deleted"


class Submission(BaseModel):
    code: str
    speakers: List[SubmissionSpeaker]
    created: Optional[datetime]  # needs organizer permissions
    title: str
    submission_type: MultiLingualStr
    submission_type_id: int
    track: Optional[MultiLingualStr]
    track_id: Optional[int]
    state: State
    pending_state: Optional[State]  # needs organizer permissions
    abstract: str
    description: str
    duration: Optional[int]
    do_not_record: bool
    is_featured: bool
    content_locale: str  # e.g. "de", "en"
    slot: Optional[Slot]  # only available after schedule release
    slot_count: int
    image: Optional[str]
    answers: Optional[List[Answer]]  # needs organizer permissions and `questions` query parameter
    notes: Optional[str]  # needs organizer permissions
    internal_notes: Optional[str]  # needs organizer permissions
    resources: List[Resource]
    tags: Optional[List[str]]  # needs organizer permissions
    tag_ids: Optional[List[int]]  # needs organizer permissions


class Talk(Submission):
    pass


class User(BaseModel):
    name: str
    email: str


class Review(BaseModel):
    id: int
    submission: str
    user: str
    text: Optional[str]
    score: Optional[float]  # converted from str if present
    created: datetime
    updated: datetime
    answers: List[str]  # ToDo: Check this type


class RoomAvailability(BaseModel):
    start: datetime
    end: datetime


class Room(BaseModel):
    id: int
    name: MultiLingualStr
    description: MultiLingualStr
    capacity: Optional[int]
    position: Optional[int]
    speaker_info: Optional[MultiLingualStr]
    availabilities: Optional[List[RoomAvailability]]  # needs organizer permissions


class QuestionRequirement(Enum):
    optional = "optional"
    required = "required"
    after_deadline = "after deadline"


class Question(BaseModel):
    id: int
    variant: str
    target: str
    question: MultiLingualStr
    help_text: MultiLingualStr
    question_required: QuestionRequirement
    deadline: Optional[datetime]
    required: bool
    read_only: Optional[bool]
    freeze_after: Optional[datetime]
    options: List[Option]
    default_answer: Optional[str]
    contains_personal_data: bool
    min_length: Optional[int]
    max_length: Optional[int]
    is_public: bool
    is_visible_to_reviewers: bool


class Tag(BaseModel):
    tag: str
    description: MultiLingualStr
    color: str
