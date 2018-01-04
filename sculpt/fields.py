from .util import nested_get, nested_has, nested_set, nested_delete, split_label
from .element import Element


class Storage(Element):
    section = None

    def __init__(self, label):
        self.label = label

    def get_cursor(self, context):
        return context.cursors[self.section]

    def set_cursor(self, context, item):
        context.cursors[self.section] = item

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.section == other.section and self.label == other.label

    @classmethod
    def compile(cls, _compiler, dct):
        return cls(label=dct["key"])


class Input(Storage):
    __el_name__ = "input"
    section = "input"

    def get(self, context):
        return nested_get(context.cursors[self.section], split_label(self.label))

    def has(self, context):
        return nested_has(context.cursors[self.section], split_label(self.label))

    def delete(self, _context):  # pylint: disable=no-self-use
        raise ValueError("delete operation not allowed on Input")

    def set(self, _context, _value):  # pylint: disable=no-self-use
        raise ValueError("set operation not allowed on Input")

    def __repr__(self):
        return "Input({})".format(self.label)


class Output(Storage):
    __el_name__ = "output"
    section = "output"

    def get(self, context):
        return nested_get(context.cursors[self.section], split_label(self.label))

    def has(self, context):
        return nested_has(context.cursors[self.section], split_label(self.label))

    def delete(self, context):
        nested_delete(context.cursors[self.section], split_label(self.label))

    def set(self, context, value):
        nested_set(context.cursors[self.section],
                   split_label(self.label), value)

    def __repr__(self):
        return "Output({})".format(self.label)


class Virtual(Storage):
    section = "virtual"

    def delete(self, context):
        if self.label in context.stores[self.section]:
            del context.stores[self.section][self.label]


class VirtualVar(Virtual):
    __el_name__ = "virtual_var"
    section = "virtual"

    def get(self, context):
        return context.stores[self.section].get(self.label)

    def has(self, context):
        return self.label in context.stores[self.section]

    def set(self, context, value):
        # virtual vars have plain namespace, so we will just
        # hit storage
        context.stores[self.section][self.label] = value

    def __repr__(self):
        return "VirtualVar({})".format(self.label)


class VirtualList(Virtual):
    __el_name__ = "virtual_list"
    context_section = "virtual"

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
