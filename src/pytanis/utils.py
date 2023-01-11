"""Additional utilities"""
from typing import Any, Dict, List, Union


def rm_keys(
    keys: Union[Any, List[Any]],
    dct: Dict[Any, Any],
) -> Dict[Any, Any]:
    """Return a copy with keys removed from dictionary"""
    if not isinstance(keys, list):
        keys = [keys]
    return {k: v for k, v in dct.items() if k not in keys}
