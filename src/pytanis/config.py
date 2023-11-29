"""Handling the configuration"""

import os
from pathlib import Path

import tomli
from pydantic import BaseModel, FilePath, validator

PYTANIS_ENV: str = 'PYTANIS_CONFIG'
"""Name of the environment variable to look up the path for the config"""
PYTANIS_CFG_PATH: str = '.pytanis/config.toml'
"""Path within $HOME to the configuration file of Pytanis"""


class Google(BaseModel):
    """Configuration related to the Google API"""

    client_secret_json: Path | None = None
    token_json: Path | None = None


class HelpDesk(BaseModel):
    """Configuration related to the HelpDesk API"""

    account: str | None = None
    entity_id: str | None = None
    token: str | None = None


class Pretalx(BaseModel):
    """Configuration related to the Pretalx API"""

    api_token: str | None = None


class Config(BaseModel):
    """Main configuration object"""

    cfg_path: FilePath

    Pretalx: Pretalx
    Google: Google
    HelpDesk: HelpDesk

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator('Google')
    @classmethod
    def convert_json_path(cls, v, values):
        def make_rel_path_abs(entry):
            if entry is not None and not entry.is_absolute():
                entry = values['cfg_path'].parent / entry
            return entry

        v.client_secret_json = make_rel_path_abs(v.client_secret_json)
        v.token_json = make_rel_path_abs(v.token_json)

        return v


def get_cfg_file() -> Path:
    """Determines the path of the config file"""
    path_str = os.environ.get(PYTANIS_ENV, None)
    path = Path.home() / Path(PYTANIS_CFG_PATH) if path_str is None else Path(path_str)
    return path


def get_cfg() -> Config:
    """Returns the configuration as an object"""
    cfg_path = get_cfg_file()
    with open(cfg_path, 'rb') as fh:
        cfg_dict = tomli.load(fh)
    # add config path to later resolve relative paths of config values
    cfg_dict['cfg_path'] = cfg_path
    return Config.parse_obj(cfg_dict)
