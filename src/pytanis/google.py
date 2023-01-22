"""Functionality around the Google API

Documentation:
    * [Google GSheet API](https://developers.google.com/sheets/api/quickstart/python)
    * [GSpread](https://docs.gspread.org/)
    * [GSpread-Dataframe](https://gspread-dataframe.readthedocs.io/)
"""
from enum import Enum
from typing import List, Optional, Union

import gspread
import pandas as pd
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from gspread_dataframe import get_as_dataframe

from .config import Config, get_cfg


class Scope(Enum):
    # Allows read-only access to the user's sheets and their properties
    GSHEET_RO = "https://www.googleapis.com/auth/spreadsheets.readonly"
    # Allows read/write access to the user's sheets and their properties
    GSHEET_RW = "https://www.googleapis.com/auth/spreadsheets"
    # Allows read-only access to the user's file metadata and file content
    GDRIVE_RO = "https://www.googleapis.com/auth/drive.readonly"
    # Per-file access to files created or opened by the app
    GDRIVE_FILE = "https://www.googleapis.com/auth/drive.file"
    # Full, permissive scope to access all of a user's files. Request this scope only when it is strictly necessary
    GDRIVE_RW = "https://www.googleapis.com/auth/drive"


def gspread_client(scopes: List[Scope], config: Config) -> gspread.client.Client:
    """Creates the GSheet client using our configuration

    Read [GSpread](https://docs.gspread.org/) for usage details
    """
    if (secret_path := config.Google.client_secret_json) is None:
        raise RuntimeError("You have to set Google.client_secret_json in your config.toml!")
    if (token_path := config.Google.token_json) is None:
        raise RuntimeError("You have to set Google.token_json in your config.toml!")

    gc = gspread.oauth(
        scopes=[scope.value for scope in scopes],
        credentials_filename=str(secret_path),
        authorized_user_filename=str(token_path),
    )
    return gc


class GoogleAPI:
    """Google API to easily handle GSheets and other files on GDrive

    By default, only the least permissive scope `GSHEET_RO` is used. Change `scopes` to have also read/write
    access but be careful with `GDRIVE_RW` that gives read/write access to ALL your files ;-)
    """

    def __init__(self, config: Optional[Config] = None, scopes: List[Scope] = [Scope.GSHEET_RO]):
        if config is None:
            config = get_cfg()
        self._config = config
        self._scopes = scopes
        self.gc = gspread_client(scopes, config)  # gspread client for more functionality

    def gsheet(self, spreadsheet_id: str, worksheet_name: Optional[str] = None) -> Union[Worksheet, Spreadsheet]:
        """Retrieve a Google sheet by its id and the name

        Open a Google sheet in your browser and check the URL to retrieve the id, e.g.:
        https://docs.google.com/spreadsheets/d/SPREEDSHEET_ID/edit...

        If the spreadsheet as several worksheets (check the lower bar) then `worksheet_name` can be used to
        specify a specific one.
        """
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        if worksheet_name is None:
            return spreadsheet
        else:
            worksheet = spreadsheet.worksheet(worksheet_name)
            return worksheet

    def gsheet_as_df(self, spreadsheet_id: str, worksheet_name: str, **kwargs) -> pd.DataFrame:
        """Returns a worksheet as dataframe"""
        worksheet = self.gsheet(spreadsheet_id, worksheet_name)
        df = get_as_dataframe(worksheet, **kwargs)
        # remove Nan rows & columns as they are exported by default
        df.dropna(how='all', inplace=True, axis=0)
        df.dropna(how='all', inplace=True, axis=1)
        return df
