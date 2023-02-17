"""Client for the Pretalx API

Documentation: https://docs.pretalx.org/api/resources/index.html

ToDo:
    * add additional parameters explicitly like querying according to the API
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union, cast

import httpx
from httpx import URL, Response
from httpx_auth import HeaderApiKey
from pydantic import BaseModel
from structlog import get_logger
from tqdm.auto import tqdm

from ..config import Config, get_cfg
from ..utils import query_params_to_dict, rm_keys, throttle
from .types import Answer, Event, Me, Question, Review, Room, Speaker, Submission, Tag, Talk

_logger = get_logger()


T = TypeVar('T', bound=BaseModel)
JSONObj = Dict[str, Any]
"""Type of a JSON object (without recursion)"""
JSONLst = List[JSONObj]
"""Type of a JSON list of JSON objects"""
JSON = Union[JSONObj, JSONLst]
"""Type of the JSON response as returned by the Pretalx API"""


class PretalxClient:
    """Client for the Pretalx API"""

    def __init__(self, config: Optional[Config] = None, blocking: bool = False):
        if config is None:
            config = get_cfg()
        self._config = config
        self._get_throttled = self._get
        self.blocking = blocking
        self.set_throttling(1, 2)  # we are nice by default

    def set_throttling(self, calls: int, seconds: int):
        """Throttle the number of calls per seconds to the Pretalx API"""
        _logger.info("throttling", calls=calls, seconds=seconds)
        self._get_throttled = throttle(calls, seconds)(self._get)

    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Response:
        """Retrieve data via GET request"""
        auth = HeaderApiKey(self._config.Pretalx.api_token, header_name='Authorization')
        url = URL("https://pretalx.com/").join(endpoint).copy_merge_params(params)
        _logger.info(f"GET: {url}")
        # we set the timeout to 60 seconds as the Pretalx API is quite slow
        return httpx.get(url, auth=auth, timeout=60.0)

    def _get_one(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> JSON:
        """Retrieve a single resource result"""
        resp = self._get_throttled(endpoint, params)
        resp.raise_for_status()
        return resp.json()

    def _resolve_pagination(self, resp: JSONObj) -> Iterator[JSONObj]:
        """Resolves the pagination and returns an iterator over all results"""
        yield from resp["results"]
        while (next_page := resp['next']) is not None:
            endpoint = URL(next_page).path
            resp = cast(JSONObj, self._get_one(endpoint, query_params_to_dict(URL(next_page).params)))
            _log_resp(resp)
            yield from resp["results"]

    def _get_many(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[JSONObj]]:
        """Retrieves the result count as well as the results as iterator"""
        resp = self._get_one(endpoint, params)
        _log_resp(resp)
        if isinstance(resp, list):
            return len(resp), iter(resp)
        elif self.blocking:
            _logger.debug("blocking resolution of pagination...")
            return resp["count"], iter(list(tqdm(self._resolve_pagination(resp), total=resp["count"])))
        else:
            _logger.debug("non-blocking resolution of pagination...")
            return resp["count"], self._resolve_pagination(resp)

    def _endpoint_lst(
        self,
        type: Type[T],
        event_slug: str,
        resource: str,
        *,
        params: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, Iterator[T]]:
        """Queries an endpoint returning a list of resources"""
        endpoint = f"/api/events/{event_slug}/{resource}/"
        count, results = self._get_many(endpoint, params)
        t_results = iter(_logger.debug("result", resp=r) or type.parse_obj(r) for r in results)
        return count, t_results

    def _endpoint_id(
        self,
        type: Type[T],
        event_slug: str,
        resource: str,
        id: Union[int, str],
        *,
        params: Optional[Dict[str, str]] = None,
    ) -> T:
        """Query an endpoint returning a single resource"""
        endpoint = f"/api/events/{event_slug}/{resource}/{id}/"
        result = self._get_one(endpoint, params)
        _logger.debug("result", resp=result)
        return type.parse_obj(result)

    def me(self) -> Me:
        """Returns what Pretalx knows about myself"""
        result = self._get_one("/api/me")
        return Me.parse_obj(result)

    def event(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Event:
        """Returns detailed information about a specific event"""
        endpoint = f"/api/events/{event_slug}/"
        result = self._get_one(endpoint, params)
        _logger.debug("result", resp=result)
        return Event.parse_obj(result)

    def events(self, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Event]]:
        """Lists all events and their details"""
        count, results = self._get_many("/api/events/", params)
        events = iter(_logger.debug("result", resp=r) or Event.parse_obj(r) for r in results)
        return count, events

    def submission(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Submission:
        """Returns a specific submission"""
        return self._endpoint_id(Submission, event_slug, "submissions", code, params=params)

    def submissions(
        self, event_slug: str, *, params: Optional[Dict[str, str]] = None
    ) -> Tuple[int, Iterator[Submission]]:
        """Lists all submissions and their details"""
        return self._endpoint_lst(Submission, event_slug, "submissions", params=params)

    def talk(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Talk:
        """Returns a specific talk"""
        return self._endpoint_id(Talk, event_slug, "talks", code, params=params)

    def talks(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Talk]]:
        """Lists all talks and their details"""
        return self._endpoint_lst(Talk, event_slug, "talks", params=params)

    def speaker(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Speaker:
        """Returns a specific speaker"""
        return self._endpoint_id(Speaker, event_slug, "speakers", code, params=params)

    def speakers(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Speaker]]:
        """Lists all speakers and their details"""
        return self._endpoint_lst(Speaker, event_slug, "speakers", params=params)

    def review(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Review:
        """Returns a specific review"""
        return self._endpoint_id(Review, event_slug, "reviews", id, params=params)

    def reviews(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Review]]:
        """Lists all reviews and their details"""
        return self._endpoint_lst(Review, event_slug, "reviews", params=params)

    def room(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Room:
        """Returns a specific room"""
        return self._endpoint_id(Room, event_slug, "rooms", id, params=params)

    def rooms(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Room]]:
        """Lists all rooms and their details"""
        return self._endpoint_lst(Room, event_slug, "rooms", params=params)

    def question(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Question:
        """Returns a specific question"""
        return self._endpoint_id(Question, event_slug, "questions", id, params=params)

    def questions(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Question]]:
        """Lists all questions and their details"""
        return self._endpoint_lst(Question, event_slug, "questions", params=params)

    def answer(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Answer:
        """Returns a specific answer"""
        return self._endpoint_id(Answer, event_slug, "answers", id, params=params)

    def answers(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Answer]]:
        """Lists all answers and their details"""
        return self._endpoint_lst(Answer, event_slug, "answers", params=params)

    def tag(self, event_slug: str, tag: str, *, params: Optional[Dict[str, str]] = None) -> Tag:
        """Returns a specific tag"""
        return self._endpoint_id(Tag, event_slug, "tags", tag, params=params)

    def tags(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Tag]]:
        """Lists all tags and their details"""
        return self._endpoint_lst(Tag, event_slug, "tags", params=params)


def _log_resp(json_resp: Union[List[Any], Dict[Any, Any]]):
    """Log everything except of the actual 'results'"""
    if isinstance(json_resp, Dict):
        _logger.debug(f"response: {rm_keys('results', json_resp)}")
