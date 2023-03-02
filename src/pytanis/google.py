"""Functionality around the Google's Spreadsheet API

Additional Documentation:
    * [Google GSheet API](https://developers.google.com/sheets/api/quickstart/python)
    * [GSpread](https://docs.gspread.org/)
    * [GSpread-Dataframe](https://gspread-dataframe.readthedocs.io/)
    * [GSpread-Formatting](https://gspread-formatting.readthedocs.io/)
"""
import string
import time
from enum import Enum
from typing import List, Optional, Tuple, Union

import gspread
import numpy as np
import pandas as pd
from gspread.client import APIError
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting import (
    Color,
    format_cell_range,
    format_cell_ranges,
    get_conditional_format_rules,
    get_default_format,
    set_data_validation_for_cell_range,
)
from gspread_formatting.dataframe import format_with_dataframe
from gspread_formatting.models import cellFormat
from matplotlib.colors import to_rgb
from structlog import get_logger

from .config import Config, get_cfg

# Color type of matplotlib: https://matplotlib.org/stable/tutorials/colors/colors.html
ColorType = Union[str, Tuple[float, float, float], Tuple[float, float, float, float]]

__all__ = ["GSheetClient", "gsheet_rows_for_fmt", "PermissionDeniedException"]

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

    def _wait_for_worksheet(self, spreadsheet_id: str, worksheet_name: str):
        """Wait for the worksheet to come into existence"""
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        while worksheet_name not in [ws.title for ws in spreadsheet.worksheets()]:
            time.sleep(1)

    def gsheet(
        self, spreadsheet_id: str, worksheet_name: Optional[str] = None, create_ws: bool = False
    ) -> Union[Worksheet, Spreadsheet]:
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
            if worksheet_name in [ws.title for ws in spreadsheet.worksheets()]:
                return spreadsheet.worksheet(worksheet_name)
            elif create_ws:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
                self._wait_for_worksheet(spreadsheet_id, worksheet_name)
                return worksheet
            else:
                return spreadsheet.worksheet(worksheet_name)  # raises exception

    def _exception_feedback(self, error: APIError):
        if error.response.json()['error']['status'] == 'PERMISSION_DENIED':
            if self._read_only:
                msg = "For saving `read_only=False` is needed when initializing this client!"
                raise PermissionDeniedException(msg) from error
            else:
                msg = "Attempt to recreate your current token by calling the method `recreate_token()` first!"
                raise PermissionDeniedException(msg) from error
        else:
            raise error

    def save_df_as_gsheet(
        self,
        df: pd.DataFrame,
        spreadsheet_id: str,
        worksheet_name: str,
        create_ws: bool = False,
        default_fmt: bool = True,
        **kwargs: Union[str, bool, int],
    ):
        """Save the given dataframe as worksheet in a spreadsheet

        Make sure that the scope passed gives you write permissions

        Args:
            df: dataframe to save
            spreadsheet_id: id of the Google spreadsheet
            worksheet_name: name of the worksheet within the spreadsheet
            create_ws: create the worksheet if non-existent
            default_fmt: apply default formatter `BasicFormatter`
            **kwargs: extra keyword arguments passed to `set_with_dataframe`
        """
        worksheet = self.gsheet(spreadsheet_id, worksheet_name, create_ws=create_ws)
        # make sure it's really only the dataframe, not some residue
        self.clear_gsheet(spreadsheet_id, worksheet_name)
        # ToDo: Starting from Python 3.9 on just use the | operator
        params = {**dict(resize=True), **dict(**kwargs)}  # set sane defaults
        try:
            set_with_dataframe(worksheet, df, **params)
            if default_fmt:
                format_with_dataframe(worksheet, df)
        except APIError as error:
            self._exception_feedback(error)

    def clear_gsheet(self, spreadsheet_id: str, worksheet_name: str):
        """Clear the worksheet including values, formatting, filtering, etc."""
        worksheet = self.gsheet(spreadsheet_id, worksheet_name, create_ws=False)
        default_fmt = get_default_format(worksheet.spreadsheet)
        range = worksheet_range(worksheet)
        try:
            worksheet.clear()
            worksheet.clear_basic_filter()
            format_cell_range(worksheet, range, default_fmt)
            rules = get_conditional_format_rules(worksheet)
            rules.clear()
            rules.save()
            set_data_validation_for_cell_range(worksheet, range, None)
        except APIError as error:
            self._exception_feedback(error)

    def gsheet_as_df(self, spreadsheet_id: str, worksheet_name: str, **kwargs: Union[str, bool, int]) -> pd.DataFrame:
        """Returns a worksheet as dataframe"""
        worksheet = self.gsheet(spreadsheet_id, worksheet_name)
        df = get_as_dataframe(worksheet, **kwargs)
        # remove Nan rows & columns as they are exported by default
        df.dropna(how='all', inplace=True, axis=0)
        df.dropna(how='all', inplace=True, axis=1)
        return df


def gsheet_col(idx: int) -> str:
    """Convert a column index to Google Sheet range notation, e.g. A, BE, etc."""
    idx += 1
    chars = []
    while idx:
        chars.append(string.ascii_uppercase[(idx % 26) - 1])
        idx //= 27
    return "".join(chars[::-1])


def gsheet_rows_for_fmt(mask: pd.Series, n_cols: int) -> List[str]:
    """Get the Google Sheet row range specifications for formatting"""
    rows = pd.Series(np.argwhere(mask.to_numpy()).reshape(-1) + 2)  # +2 since 1-index and header
    last_col = gsheet_col(n_cols - 1)  # last index
    rows = rows.map(lambda x: f"A{x}:{last_col}{x}")
    return rows.to_list()


def worksheet_range(worksheet: Worksheet) -> str:
    """Returns a range encompassing the whole worksheet"""
    last_row = worksheet.row_count
    last_col = gsheet_col(worksheet.col_count)
    return f"A1:{last_col}{last_row}"


def mark_rows(worksheet, mask: pd.Series, color: ColorType):
    """Mark rows specified by a mask (condition) with a given color

    Color can be a tuple of RGB values or a Matplotlib string specification:
    https://matplotlib.org/stable/gallery/color/named_colors.html#css-colors
    """
    rows = gsheet_rows_for_fmt(mask, worksheet.col_count)
    fmt = cellFormat(backgroundColor=Color(*to_rgb(color)))
    if rows:
        format_cell_ranges(worksheet, [(rng, fmt) for rng in rows])
