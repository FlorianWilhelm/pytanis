"""Additional utilities"""
import functools
import time
from math import fabs
from typing import Any, Dict, List, Union


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


def throttle(calls: int, seconds: int = 1):
    """Decorator for throttling a function to number of calls per seconds

    Args:
        calls: number of calls per interval
        seconds: number of seconds in interval

    Returns:
        wrapped function
    """
    assert isinstance(calls, int), 'number of calls must be integer'
    assert isinstance(seconds, int), 'number of seconds must be integer'

    def wraps(func):
        # keeps track of the last calls
        last_calls = list()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            curr_time = time.time()
            if last_calls:
                # remove calls from last_calls list older than interval in seconds
                idx_old_calls = [i for i, t in enumerate(last_calls) if t < curr_time - seconds]
                if idx_old_calls:
                    del last_calls[: idx_old_calls[-1]]
            if len(last_calls) >= calls:
                idx = len(last_calls) - calls
                delta = fabs(1 - curr_time + last_calls[idx])
                # logger = logging.getLogger(func.__module__)
                # logger.debug("Stalling call to {} for {}s".format(func.__name__, delta))
                time.sleep(delta)
            resp = func(*args, **kwargs)
            last_calls.append(time.time())
            return resp

        return wrapper

    return wraps
