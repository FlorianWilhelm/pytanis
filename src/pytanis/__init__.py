from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pytanis")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = ["__version__"]
