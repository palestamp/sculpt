from functools import reduce
from operator import getitem


class InfoDict(dict):
    def __init__(self, *args, **kwargs):
        super(InfoDict, self).__init__(*args, **kwargs)
        self.lineno = None


def nested_access(dct, keys):
    try:
        return True, reduce(getitem, keys, dct)
    except KeyError:
        return False, None


def nested_get(dct, keys):
    _, value = nested_access(dct, keys)
    return value


def nested_has(dct, keys):
    exists, _ = nested_access(dct, keys)
    return exists
