"""Client for the HelpDesk / LiveChat API

Documentation: https://api.helpdesk.com/docs

ToDo:
    * Transfer more functionality from https://github.com/PYCONDE/py_helpdesk_com
"""
from typing import Any, Dict, List, Optional, Union

import httpx
from httpx import URL, Response
from httpx_auth import Basic
from structlog import get_logger

from ..config import Config, get_cfg
from ..utils import throttle
from .types import Agent, NewTicket, Team

_logger = get_logger()


JSONObj = Dict[str, Any]
"""Type of a JSON object (without recursion)"""
JSONLst = List[JSONObj]
"""Type of a JSON list of JSON objects"""
JSON = Union[JSONObj, JSONLst]
"""Type of the JSON response as returned by the HelpDesk / LiveChat API"""


class HelpDeskClient:
    def __init__(self, config: Optional[Config] = None):
        if config is None:
            config = get_cfg()
        self._config = config
        # Important: Always use a custom User-Agent, never a generic one.
        # Generic User-Agents are filtered by helpdesk to reduce spam.
        self._headers = {"User-Agent": "Pytanis"}

        self._get_throttled = self._get
        self._post_throttled = self._post
        self.set_throttling(2, 1)  # we are nice by default

    def set_throttling(self, calls: int, seconds: int):
        """Throttle the number of calls per seconds to the Pretalx API"""
        _logger.debug("throttling", calls=calls, seconds=seconds)
        self._get_throttled = throttle(calls, seconds)(self._get)
        self._post_throttled = throttle(calls, seconds)(self._post)

    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Response:
        """Retrieve data via raw GET request"""
        auth = Basic(self._config.HelpDesk.account, self._config.HelpDesk.token)
        url = URL("https://api.helpdesk.com/v1/").join(endpoint)
        _logger.debug(f"GET: {url.copy_merge_params(params)}")
        return httpx.get(url, auth=auth, params=params, headers=self._headers)

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> JSON:
        """Retrieve data via throttled GET request and return the JSON"""
        resp = self._get_throttled(endpoint, params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, str]] = None) -> Response:
        """Sent data via raw POST request"""
        auth = Basic(self._config.HelpDesk.account, self._config.HelpDesk.token)
        url = URL("https://api.helpdesk.com/v1/").join(endpoint)
        _logger.debug(f"POST: {url.copy_merge_params(params)}")
        return httpx.post(url, auth=auth, params=params, json=data, headers=self._headers)

    def post(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, str]] = None) -> JSON:
        resp = self._post_throttled(endpoint, data, params)
        resp.raise_for_status()
        return resp.json()

    def list_agents(self) -> List[Agent]:
        agents = self.get("agents")
        assert isinstance(agents, List)
        return [Agent.parse_obj(dct) for dct in agents]

    def list_teams(self) -> List[Team]:
        teams = self.get("teams")
        assert isinstance(teams, List)
        return [Team.parse_obj(dct) for dct in teams]

    def create_ticket(self, ticket: NewTicket):
        return self.post("tickets", data=ticket.dict())
