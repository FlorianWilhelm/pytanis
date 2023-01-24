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
from gspread.client import APIError
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from structlog import get_logger

from .config import Config, get_cfg

_logger = get_logger()


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


class PermissionDeniedException(Exception):
    """Exception for APIError with status PERMISSION_DENIED

    Most likely thrown in cases when the scope is not `GSHEET_RW` or the token needs to be updated accordingly.
    """


class GSheetClient:
    """Google API to easily handle GSheets and other files on GDrive

    By default, only the least permissive scope `GSHEET_RO` in case of `read_only = True` is used.
    """

    def __init__(self, config: Optional[Config] = None, read_only: bool = True):
        self._read_only = read_only
        if read_only:
            self._scopes = [Scope.GSHEET_RO]
        else:
            self._scopes = [Scope.GSHEET_RW]
        if config is None:
            config = get_cfg()
        self._config = config
        self.gc = gspread_client(self._scopes, config)  # gspread client for more functionality

    def recreate_token(self):
        """Recreate the current token using the scopes given at initialization"""
        self._config.Google.token_json.unlink(missing_ok=True)
        self.gc = gspread_client(self._scopes, self._config)

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

    def save_df_as_gsheet(self, df: pd.DataFrame, spreadsheet_id: str, worksheet_name: str, **kwargs):
        """Save the given dataframe as worksheet in a spreadsheet

        Make sure that the scope passed gives you write permissions

        Args:
            df: dataframe to save
            spreadsheet_id: id of the Google spreadsheet
            worksheet_name: name of the worksheet within the spreadsheet
            **kwargs: extra keyword arguments passed to `set_with_dataframe`
        """
        worksheet = self.gsheet(spreadsheet_id, worksheet_name)
        try:
            worksheet.clear()  # make sure it's really only the dataframe, not some residue
            set_with_dataframe(worksheet, df, **kwargs)
        except APIError as e:
            if e.response.json()['error']['status'] == 'PERMISSION_DENIED':
                if self._read_only:
                    msg = "For saving `read_only=False` is needed when initializing this client!"
                    raise PermissionDeniedException(msg) from e
                else:
                    msg = "Attempt to recreate your current token by calling the method `recreate_token()` first!"
                    raise PermissionDeniedException(msg) from e
            else:
                raise e

    def gsheet_as_df(self, spreadsheet_id: str, worksheet_name: str, **kwargs: Union[str, bool, int]) -> pd.DataFrame:
        """Returns a worksheet as dataframe"""
        worksheet = self.gsheet(spreadsheet_id, worksheet_name)
        df = get_as_dataframe(worksheet, **kwargs)
        # remove Nan rows & columns as they are exported by default
        df.dropna(how='all', inplace=True, axis=0)
        df.dropna(how='all', inplace=True, axis=1)
        return df
