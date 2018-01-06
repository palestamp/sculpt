import functools

from .util import (nested_get, nested_has, nested_set, nested_delete,
                   split_label, classproperty)
from .element import Element


def with_cursor(func):
    @functools.wraps(func)
    def wrapper(self, context, *args, **kwargs):
        cursors = self.get_cursor(context)
        kwargs["cursor"] = cursors
        return func(self, context, *args, **kwargs)
    return wrapper


class Storage(Element):
    __context_section__ = None
    __eq_attrs__ = ["section", "label"]

    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (self.section == other.section and
                self.label == other.label)

    @classproperty
    def section(cls):  # pylint: disable=no-self-argument
        return cls.__context_section__

    def get_cursor(self, context):
        return context.cursors[self.section]

    def set_cursor(self, context, item):
        context.cursors[self.section] = item

    @classmethod
    def compile(cls, _compiler, dct):
        return cls(label=dct["key"])


class Input(Storage):
    __context_section__ = "input"

    @with_cursor
    def get(self, _context, cursor):
        return nested_get(cursor, split_label(self.label))
    
    @with_cursor
    def has(self, _context, cursor):
        return nested_has(cursor, split_label(self.label))

    def delete(self, _context):  # pylint: disable=no-self-use
        raise ValueError("delete operation not allowed on Input")

    def set(self, _context, _value):  # pylint: disable=no-self-use
        raise ValueError("set operation not allowed on Input")

    def accept(self, visitor):
        return visitor.visit_input(self)

    def __repr__(self):
        return "Input({})".format(self.label)


class Output(Storage):
    __context_section__ = "output"

    @with_cursor
    def get(self, _context, cursor):
        return nested_get(cursor, split_label(self.label))

    @with_cursor
    def has(self, _context, cursor):
        return nested_has(cursor, split_label(self.label))

    @with_cursor
    def delete(self, _context, cursor):
        nested_delete(cursor, split_label(self.label))

    @with_cursor
    def set(self, _context, value, cursor):
        nested_set(cursor, split_label(self.label), value)

    def accept(self, visitor):
        return visitor.visit_output(self)

    def __repr__(self):
        return "Output({})".format(self.label)


class Virtual(Storage):
    __context_section__ = "virtual"

    def delete(self, context):
        if self.label in context.stores[self.section]:
            del context.stores[self.section][self.label]


class VirtualVar(Virtual):
    def get(self, context):
        return context.stores[self.section].get(self.label)

    def has(self, context):
        return self.label in context.stores[self.section]

    def set(self, context, value):
        # virtual vars have plain namespace, so we will just
        # hit storage
        context.stores[self.section][self.label] = value

    def accept(self, visitor):
        return visitor.visit_virtual_var(self)

    def __repr__(self):
        return "VirtualVar({})".format(self.label)


class VirtualList(Virtual):
    def __init__(self, label, _op="set"):
        super(VirtualList, self).__init__(label)
        self._op = _op
        self.cbs = []

    def get(self, context):
        val = context.stores[self.section].get(self.label, [])
        for callback in self.cbs:
            val = callback(val)
        return val

    def has(self, context):
        return self.label in context.stores[self.section]

    def set(self, ctx, val):
        if self._op == "set":
            self._assign_set(ctx, val)
        elif self._op == "append":
            self._assign_append(ctx, val)
        elif self._op == "extend":
            self._assign_extend(ctx, val)

    def accept(self, visitor):
        return visitor.visit_virtual_list(self)

    def append(self):
        return self.__class__(self.label, _op="append")

    def extend(self):
        return self.__class__(self.label, _op="extend")

    def map(self, callback):
        def _map(_list):
            return list(map(callback, _list))
        self.cbs.append(_map)
        return self

    def find(self, _filter):
        def _find(_list):
            for item in _list:
                if _filter(item):
                    return item
            return None

        self.cbs.append(_find)
        return self

    def _assign_set(self, context, value):
        if not isinstance(value, list):
            raise TypeError("expected list, got %s" % type(value))

        context.stores[self.section][self.label] = value

    def _assign_append(self, context, value):
        current = self.get(context)
        if isinstance(current, list):
            current.append(value)
        else:
            current = [value]

        self._assign_set(context, current)

    def _assign_extend(self, context, value):
        current = self.get(context)
        if not isinstance(value, list):
            raise TypeError("expected list, got %s" % type(value))

        if isinstance(current, list):
            current.extend(value)
        else:
            current = [value]

        self._assign_set(context, current)
