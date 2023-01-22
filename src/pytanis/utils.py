"""Additional utilities"""
import functools
import time
from math import fabs
from typing import Any, Callable, Dict, List, TypeVar, Union

import pandas as pd
from structlog import get_logger

RT = TypeVar('RT')  # return type


def rm_keys(
    keys: Union[Any, List[Any]],
    dct: Dict[Any, Any],
) -> Dict[Any, Any]:
    """Return a copy with keys removed from dictionary"""
    if not isinstance(keys, list):
        keys = [keys]
    return {k: v for k, v in dct.items() if k not in keys}


def pretty_timedelta(seconds: int) -> str:
    """Converts timedelta in seconds to human-readable string

    Args:
        seconds: time delta in seconds

    Returns:
        timedelta as pretty string
    """
    sign = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '{}{}d{}h{}m{}s'.format(sign, days, hours, minutes, seconds)
    elif hours > 0:
        return '{}{}h{}m{}s'.format(sign, hours, minutes, seconds)
    elif minutes > 0:
        return '{}{}m{}s'.format(sign, minutes, seconds)
    else:
        return '{}{}s'.format(sign, seconds)


def throttle(calls: int, seconds: int = 1) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Decorator for throttling a function to number of calls per seconds

    Args:
        calls: number of calls per interval
        seconds: number of seconds in interval

    Returns:
        wrapped function
    """
    assert isinstance(calls, int), 'number of calls must be integer'
    assert isinstance(seconds, int), 'number of seconds must be integer'

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        # keeps track of the last calls
        last_calls: List[float] = list()

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> RT:
            curr_time = time.time()
            if last_calls:
                # remove calls from last_calls list older than interval in seconds
                idx_old_calls = [i for i, t in enumerate(last_calls) if t < curr_time - seconds]
                if idx_old_calls:
                    del last_calls[: idx_old_calls[-1]]
            if len(last_calls) >= calls:
                idx = len(last_calls) - calls
                delta = fabs(1 - curr_time + last_calls[idx])
                logger = get_logger()
                logger.debug("stalling call", func=func.__name__, secs=delta)
                time.sleep(delta)
            resp = func(*args, **kwargs)
            last_calls.append(time.time())
            return resp

        return wrapper

    return decorator


def implode(df: pd.DataFrame, cols: Union[str, List[str]]) -> pd.DataFrame:
    """The inverse of Pandas' explode"""
    if not isinstance(cols, list):
        cols = [cols]
    orig_cols = df.columns
    grp_cols = [col for col in df.columns if col not in cols]
    df = df.groupby(grp_cols, group_keys=True, dropna=False).aggregate({col: lambda x: x.tolist() for col in cols})
    df.reset_index(inplace=True)
    df = df.loc[:, orig_cols]
    return df
