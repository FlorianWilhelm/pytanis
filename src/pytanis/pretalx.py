"""Functionality around Pretalx API

Documentation: https://docs.pretalx.org/api/
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import httpx
from httpx import URL, Response
from structlog import get_logger

from .config import Config, get_cfg
from .utils import rm_keys

logger = get_logger()


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

    def _get_pages(self, resp: Response) -> Iterator[Dict[str, Any]]:
        """Resolves the pagination and returns an iterator"""
        yield from resp["results"]
        # resolve pagination
        while (next_page := resp['next']) is not None:
            endpoint = URL(next_page).path
            resp = self._get(endpoint, dict(URL(next_page).params)).json()
            _log_resp(resp)
            yield from resp["results"]

    def retrieve(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Tuple[int, Iterator[Dict[str, Any]]]:
        """Retrieves the number of result as well as the result as iterator"""
        resp = self._get(endpoint, params).json()
        _log_resp(resp)
        if isinstance(resp, list):
            return len(resp), iter(resp)
        else:  # pagination
            return resp["count"], self._get_pages(resp)

    def get_events(self) -> Tuple[int, Iterator[Dict[str, Any]]]:
        return self.retrieve("/api/events/")

    def get_submissions(self, event_slug) -> Tuple[int, Iterator[Dict[str, Any]]]:
        return self.retrieve(f"api/events/{event_slug}/submissions/")


def _log_resp(json_resp: Union[List[Any], Dict[Any, Any]]):
    if isinstance(json_resp, Dict):
        logger.debug(f"response: {rm_keys('results', json_resp)}")
