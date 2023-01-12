"""Functionality around Pretalx API

Documentation: https://docs.pretalx.org/api/

ToDo:
    * Split types and API into own modules within subpackage
    * have separate methods for list and specific resources
    * add additional parameters explicitely like querying according to the API
"""
import re
from datetime import date, datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

import httpx
from httpx import URL, Response
from pydantic import BaseModel, Extra, Field
from structlog import get_logger

from .config import Config, get_cfg
from .utils import rm_keys

logger = get_logger()

T = TypeVar('T', bound=BaseModel)
JSONObj = Dict[str, Any]
JSONLst = List[JSONObj]
JSON = Union[JSONObj, JSONLst]
"""Stub for the JSON response as returned by the Pretalx API"""


class MultiLingualStr(BaseModel, extra=Extra.allow):
    # ToDo: Add here more available languages, not mentioned in the API
    en: Optional[str]
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
    # ToDo: Check the datatypes here again, not mentioned in the API
    id: int
    option: str


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
    submissions: list[str]  # submission codes
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


class Submission(BaseModel):
    code: str
    speakers: List[SubmissionSpeaker]
    created: Optional[datetime]  # needs organizer permissions
    title: str
    submission_type: MultiLingualStr
    submission_type_id: int
    track: Optional[MultiLingualStr]
    track_id: Optional[int]
    state: str
    pending_state: Optional[str]  # needs organizer permissions
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
    user: str  # but says 'name' and 'email' in the API docs
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


class Question(BaseModel):
    id: int
    variant: str
    target: str
    question: MultiLingualStr
    help_text: MultiLingualStr
    question_required: str  # from [optional, required, after_deadline] ToDo: handle as enum?
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


class PretalxAPI:
    def __init__(self, config: Optional[Config] = None):
        if config is None:
            config = get_cfg()
        self.config = config

    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Response:
        """Retrieve data via GET request"""
        header = {'Authorization': self.config.Pretalx.api_token}
        url = URL("https://pretalx.com/").join(endpoint)
        logger.debug(f"request: {url.copy_merge_params(params)}")
        return httpx.get(url, headers=header, params=params)

    def _get_single(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> JSON:
        """Retrieve a single resource result"""
        resp = self._get(endpoint, params)
        resp.raise_for_status()
        return resp.json()

    def _resolve_pagination(self, resp: JSONObj) -> Iterator[JSONObj]:
        """Resolves the pagination and returns an iterator over all results"""
        yield from resp["results"]
        while (next_page := resp['next']) is not None:
            endpoint = URL(next_page).path
            resp = self._get_single(endpoint, dict(URL(next_page).params))
            _log_resp(resp)
            yield from resp["results"]

    def _get_many(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[JSONObj]]:
        """Retrieves the number of results as well as the results as iterator"""
        resp = self._get_single(endpoint, params)
        _log_resp(resp)
        if isinstance(resp, list):
            return len(resp), iter(resp)
        else:
            logger.debug("Resolving pagination...")
            return resp["count"], self._resolve_pagination(resp)

    def _endpoint(
        self,
        type: Type[T],
        event_slug: Optional[str] = None,
        resource: Optional[str] = None,
        id: Optional[Union[str, int]] = None,
        *,
        params: Optional[Dict[str, str]] = None,
    ) -> Union[T, Tuple[int, Iterator[T]]]:
        """Query the endpoint given potentially an event, resource and some resource id"""
        event_slug = '' if event_slug is None else event_slug
        resource = '' if resource is None else resource
        id = '' if id is None else id
        endpoint = re.sub("//+", "/", f"/api/events/{event_slug}/{resource}/{id}/")

        if id:
            return type.parse_obj(self._get_single(endpoint, params))
        elif resource:
            count, results = self._get_many(endpoint, params)
            return count, (type.parse_obj(r) for r in results)

        elif event_slug:
            return type.parse_obj(self._get_single(endpoint, params))
        else:
            count, results = self._get_many(endpoint, params)
            return count, (type.parse_obj(r) for r in results)

    def events(self, event_slug: Optional[str] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Event, event_slug, params=params)

    def submissions(self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Submission, event_slug, "submissions", code, params=params)

    def talks(self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Talk, event_slug, "talks", code, params=params)

    def speakers(self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Speaker, event_slug, "speakers", code, params=params)

    def reviews(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Review, event_slug, "reviews", id, params=params)

    def rooms(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Room, event_slug, "rooms", id, params=params)

    def questions(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Question, event_slug, "questions", id, params=params)

    def answers(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Answer, event_slug, "answers", id, params=params)

    def tags(self, event_slug: str, tag: Optional[str] = None, *, params: Optional[Dict[str, str]] = None):
        return self._endpoint(Tag, event_slug, "tags", tag, params=params)


def _log_resp(json_resp: Union[List[Any], Dict[Any, Any]]):
    if isinstance(json_resp, Dict):
        logger.debug(f"response: {rm_keys('results', json_resp)}")
