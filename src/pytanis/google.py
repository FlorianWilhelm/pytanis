"""Functionality around the Google API

Documentation: https://developers.google.com/sheets/api/quickstart/python
"""
import itertools
from typing import Any, Dict, List, Optional

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import Config, get_cfg

RO_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class GoogleAPI:
    def __init__(self, config: Optional[Config] = None, scopes: List[str] = RO_SCOPE):
        if config is None:
            config = get_cfg()
        self.config = config
        self.scopes = scopes

    def init_token(self, recreate: bool = False):
        """Init the API token by creating it if not available

        Remember to recreate the token everytime you change the scopes.
        This function will open a browser window for authentication.
        """
        if (token_path := self.config.Google.token_json) is None:
            raise RuntimeError("You have to Google.token_json in your config.toml!")
        if not recreate and token_path.exists():
            return

        secret_path = self.config.Google.client_secret_json
        flow = InstalledAppFlow.from_client_secrets_file(secret_path, self.scopes)
        creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as fh:
            fh.write(creds.to_json())

    def _get_creds(self) -> Credentials:
        """Retrieve the credentials"""
        token_path = self.config.Google.token_json
        if token_path is None or not token_path.exists():
            raise RuntimeError(f"Necessary token {token_path} does not exist!")
        creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    def gsheet(self, spreadsheet_id: str, range: str, **kwargs) -> Dict[str, Any]:
        """Retrieve a google sheet"""
        creds = self._get_creds()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
        gsheet = sheet.values().get(spreadsheetId=spreadsheet_id, range=range, **kwargs).execute()
        return gsheet

    def gsheet_as_df(self, spreadsheet_id: str, range: str, header: bool = True) -> pd.DataFrame:
        gsheet = self.gsheet(spreadsheet_id, range, majorDimension="COLUMNS")
        return gsheet_to_df(gsheet, header)


def gsheet_to_df(gsheet: Dict[str, Any], header: bool = True) -> pd.DataFrame:
    """Transform a Google Sheet into a Pandas DataFrame

    Requires a gsheet with columns as major dimension
    """
    values = gsheet.get('values', [])
    if not values:
        return pd.DataFrame()
    if header:
        columns = [col.pop(0) for col in values]
    else:
        columns = list(range(len(values)))

    padded_values = zip(*itertools.zip_longest(*values, fillvalue=''))
    data = {col: val for col, val in zip(columns, padded_values)}
    return pd.DataFrame(data)
