"""Functionality around Pretalx API

Documentation: https://docs.pretalx.org/api/
"""
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import httpx
from httpx import URL, Response
from structlog import get_logger

from .config import Config, get_cfg
from .utils import rm_keys

logger = get_logger()

JSONObj = Dict[str, Any]
JSONLst = List[JSONObj]
JSON = Union[JSONObj, JSONLst]
"""Stub for the JSON response as returned by the Pretalx API"""


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
        event_slug: Optional[str] = None,
        resource: Optional[str] = None,
        id: Optional[Union[str, int]] = None,
        *,
        params: Optional[Dict[str, str]] = None,
    ) -> Union[JSONObj, Tuple[int, Iterator[JSONObj]]]:
        """Query the endpoint given potentially an event, resource and some resource id"""
        event_slug = '' if event_slug is None else event_slug
        resource = '' if resource is None else resource
        id = '' if id is None else id
        endpoint = re.sub("//+", "/", f"/api/events/{event_slug}/{resource}/{id}/")

        if id:
            return self._get_single(endpoint, params)
        elif resource:
            return self._get_many(endpoint, params)
        elif event_slug:
            return self._get_single(endpoint, params)
        else:
            return self._get_many(endpoint, params)

    def events(self, event_slug: Optional[str] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, params=params)

    def submissions(
        self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None
    ) -> JSON:
        return self._endpoint(event_slug, "submissions", code, params=params)

    def talks(self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "talks", code, params=params)

    def speakers(self, event_slug: str, code: Optional[str] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "speakers", code, params=params)

    def reviews(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "reviews", id, params=params)

    def rooms(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "rooms", id, params=params)

    def questions(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "questions", id, params=params)

    def answers(self, event_slug: str, id: Optional[int] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "answers", id, params=params)

    def tags(self, event_slug: str, tag: Optional[str] = None, *, params: Optional[Dict[str, str]] = None) -> JSON:
        return self._endpoint(event_slug, "tags", tag, params=params)


def _log_resp(json_resp: Union[List[Any], Dict[Any, Any]]):
    if isinstance(json_resp, Dict):
        logger.debug(f"response: {rm_keys('results', json_resp)}")
