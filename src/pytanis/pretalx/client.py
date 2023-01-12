"""Client for the Pretalx API

Documentation: https://docs.pretalx.org/api/

ToDo:
    * add additional parameters explicitly like querying according to the API
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

import httpx
from httpx import URL, Response
from pydantic import BaseModel
from structlog import get_logger

from ..config import Config, get_cfg
from ..utils import rm_keys, throttle
from .types import Answer, Event, Me, Question, Review, Room, Speaker, Submission, Tag, Talk

logger = get_logger()


T = TypeVar('T', bound=BaseModel)
JSONObj = Dict[str, Any]
JSONLst = List[JSONObj]
JSON = Union[JSONObj, JSONLst]
"""Stub for the JSON response as returned by the Pretalx API"""


class PretalxAPI:
    def __init__(self, config: Optional[Config] = None):
        if config is None:
            config = get_cfg()
        self.config = config
        self._get_orig = self._get
        self.set_throttling(1, 2)  # we are nice by default

    def set_throttling(self, calls: int, seconds: int):
        """Throttle the number of calls per seconds to the Pretalx API"""
        logger.debug("throttling", calls=calls, seconds=seconds)
        self._get = throttle(calls, seconds)(self._get_orig)

    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Response:
        """Retrieve data via GET request"""
        header = {'Authorization': self.config.Pretalx.api_token}
        url = URL("https://pretalx.com/").join(endpoint)
        logger.debug(f"request: {url.copy_merge_params(params)}")
        return httpx.get(url, headers=header, params=params)

    def _get_one(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> JSON:
        """Retrieve a single resource result"""
        resp = self._get(endpoint, params)
        resp.raise_for_status()
        return resp.json()

    def _resolve_pagination(self, resp: JSONObj) -> Iterator[JSONObj]:
        """Resolves the pagination and returns an iterator over all results"""
        yield from resp["results"]
        while (next_page := resp['next']) is not None:
            endpoint = URL(next_page).path
            resp = self._get_one(endpoint, dict(URL(next_page).params))
            _log_resp(resp)
            yield from resp["results"]

    def _get_many(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[JSONObj]]:
        """Retrieves the number of results as well as the results as iterator"""
        resp = self._get_one(endpoint, params)
        _log_resp(resp)
        if isinstance(resp, list):
            return len(resp), iter(resp)
        else:
            logger.debug("Resolving pagination...")
            return resp["count"], self._resolve_pagination(resp)

    def _endpoint_lst(
        self,
        type: Type[T],
        event_slug: str,
        resource: str,
        *,
        params: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, Iterator[T]]:
        """Query an endpoint returning a list of resources"""
        endpoint = f"/api/events/{event_slug}/{resource}/"
        count, results = self._get_many(endpoint, params)
        # parse according to the Pretalx API type and debug
        results = ((logger.debug("result", resp=r), type.parse_obj(r))[1] for r in results)
        return count, results

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
        logger.debug("result", resp=result)
        return type.parse_obj(result)

    def me(self) -> Me:
        result = self._get_one("/api/me")
        return Me.parse_obj(result)

    def event(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Event:
        endpoint = f"/api/events/{event_slug}/"
        result = self._get_one(endpoint, params)
        logger.debug("result", resp=result)
        return Event.parse_obj(result)

    def events(self, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Event]]:
        count, results = self._get_many("/api/events/", params)
        results = ((logger.debug("result", resp=r), Event.parse_obj(r))[1] for r in results)
        return count, results

    def submission(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Submission:
        return self._endpoint_id(Submission, event_slug, "submissions", code, params=params)

    def submissions(
        self, event_slug: str, *, params: Optional[Dict[str, str]] = None
    ) -> Tuple[int, Iterator[Submission]]:
        return self._endpoint_lst(Submission, event_slug, "submissions", params=params)

    def talk(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Talk:
        return self._endpoint_id(Talk, event_slug, "talks", code, params=params)

    def talks(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Talk]]:
        return self._endpoint_lst(Talk, event_slug, "talks", params=params)

    def speaker(self, event_slug: str, code: str, *, params: Optional[Dict[str, str]] = None) -> Speaker:
        return self._endpoint_id(Speaker, event_slug, "speakers", code, params=params)

    def speakers(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Speaker]]:
        return self._endpoint_lst(Speaker, event_slug, "speakers", params=params)

    def review(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Review:
        return self._endpoint_id(Review, event_slug, "reviews", id, params=params)

    def reviews(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Review]]:
        return self._endpoint_lst(Review, event_slug, "reviews", params=params)

    def room(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Room:
        return self._endpoint_id(Room, event_slug, "rooms", id, params=params)

    def rooms(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Room]]:
        return self._endpoint_lst(Room, event_slug, "rooms", params=params)

    def question(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Question:
        return self._endpoint_id(Question, event_slug, "questions", id, params=params)

    def questions(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Question]]:
        return self._endpoint_lst(Question, event_slug, "questions", params=params)

    def answer(self, event_slug: str, id: int, *, params: Optional[Dict[str, str]] = None) -> Answer:
        return self._endpoint_id(Answer, event_slug, "answers", id, params=params)

    def answers(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Answer]]:
        return self._endpoint_lst(Answer, event_slug, "answers", params=params)

    def tag(self, event_slug: str, tag: str, *, params: Optional[Dict[str, str]] = None) -> Tag:
        return self._endpoint_id(Tag, event_slug, "tags", tag, params=params)

    def tags(self, event_slug: str, *, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Tag]]:
        return self._endpoint_lst(Tag, event_slug, "tags", params=params)


def _log_resp(json_resp: Union[List[Any], Dict[Any, Any]]):
    if isinstance(json_resp, Dict):
        logger.debug(f"response: {rm_keys('results', json_resp)}")
