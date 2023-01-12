from importlib.metadata import PackageNotFoundError, version

import structlog

from .google import GoogleAPI
from .pretalx import PretalxAPI

try:
    __version__ = version("pytanis")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = ["__version__", "GoogleAPI", "PretalxAPI"]

# transform structlog into a logging-friendly package
structlog.stdlib.recreate_defaults()
