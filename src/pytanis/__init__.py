from importlib.metadata import PackageNotFoundError, version

import structlog

from pytanis.pretalx.client import PretalxAPI

from .google import GoogleAPI

try:
    __version__ = version("pytanis")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = ["__version__", "GoogleAPI", "PretalxAPI"]

# transform structlog into a logging-friendly package
structlog.stdlib.recreate_defaults()
