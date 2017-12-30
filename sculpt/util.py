from operator import getitem
from functools import reduce

try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

def _nested_access(dct, keys):
    try:
        return reduce(getitem, keys, dct), True
    except KeyError:
        return None, False


def nested_get(dct, keys):
    value, _ = _nested_access(dct, keys)
    return value


def nested_has(dct, keys):
    _, exists = _nested_access(dct, keys)
    return exists


def nested_delete(dct, keys):
    if not keys:
        return

    parent_path = keys[:-1]
    key = keys[-1]
    target = nested_get(dct, parent_path)
    if isinstance(target, dict):
        del target[key]


def nested_set(dct, keys, value):
    leaf = reduce(lambda d, k: d.setdefault(k, {}), keys[:-1], dct)
    leaf[keys[-1]] = value


def split_label(label):
    return label.split(".")
