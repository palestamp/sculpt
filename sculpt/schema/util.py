
from collections import UserDict
from functools import reduce
from operator import getitem


class InfoDict(UserDict):
    def __init__(self, *args, **kwargs):
        super(InfoDict, self).__init__(*args, **kwargs)
        self.lineno = None


def _nested_access(dct, keys):
    try:
        return reduce(getitem, keys, dct), True
    except KeyError:
        return None, False


def nested_get(dct, keys):
    value, _ = _nested_access(dct, keys)
    return value
