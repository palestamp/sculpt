from functools import reduce
from operator import getitem
try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

from .validation import ValidationError


class Storage(object):
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
    context_section = "virtual"

    def __init__(self, label, _op="set"):
        self.label = label
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


class Context(object):
    def __init__(self, _input):
        self.stores = {
            Input.section: _input,
            Output.section: {},
            Virtual.section: {},
        }

        self.cursors = {
            Input.section: self.stores[Input.section],
            Output.section: self.stores[Output.section],
            Virtual.section: self.stores[Virtual.section],
        }

        self.errors = []


class Copy(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

        # static check for Input assignment
        if isinstance(self.right, Input):
            # just trigger Input.set which should raise
            # XXX: strange decision...
            self.right.set(None, None)

    def run(self, context):
        value = self.left.get(context)

        # ignore field if it not exists
        if value is None and not self.left.has(context):
            return

        self.right.set(context, value)

    @classmethod
    def compile(cls, compiler, dct):
        left = compiler.load_field(dct["left"])
        right = compiler.load_field(dct["right"])
        return cls(left=left, right=right)

    def __repr__(self):
        return "Copy({}, {})".format(self.left, self.right)


class Apply(object):
    def __init__(self, field, function):
        self.field = field
        self.function = function

    def run(self, context):
        value = self.field.get(context)
        self.field.set(context, self.function(value))

    @classmethod
    def compile(cls, compiler, dct):
        field = compiler.load_field(dct["field"])
        func = dct["func"]
        return cls(field=field, function=func)

    def __repr__(self):
        try:
            function_name = self.function.__name__
        except AttributeError:
            function_name = "function"
        return "Apply({}, {})".format(self.field, function_name)


class Combine(object):
    def __init__(self, *actions):
        self.actions = actions

    def run(self, _context):
        return self.actions

    @classmethod
    def compile(cls, compiler, dct):
        ops = dct["ops"]
        ops = [compiler.load_operation(op) for op in ops]
        return cls(*ops)

    def __repr__(self):
        rs = ", ".join([str(op) for op in self.actions])
        return "Combine({})".format(rs)


class Delete(object):
    def __init__(self, field):
        self.field = field

    def run(self, context):
        self.field.delete(context)


class Each(object):
    def __init__(self, left, right, actions):
        self.left = left
        self.right = right
        self.actions = actions

    def run(self, context):
        # grab producer node
        left_list = self.left.get(context)
        right_list = []

        old_left_cursor = self.left.get_cursor(context)
        old_right_cursor = self.right.get_cursor(context)

        for item in left_list:
            self.left.set_cursor(context, item)
            self.right.set_cursor(context, {})
            run_actions(context, self.actions)
            right_list.append(self.right.get_cursor(context))

        self.left.set_cursor(context, old_left_cursor)
        self.right.set_cursor(context, old_right_cursor)
        self.right.set(context, right_list)


class With(object):
    def __init__(self, left, right, actions):
        self.left = left
        self.right = right
        self.actions = actions

    def run(self, context):
        # get value by path
        left_object = self.left.get(context)
        right_object = {}

        # remember old cursor positions
        old_left_cursor = self.left.get_cursor(context)
        old_right_cursor = self.right.get_cursor(context)

        # set new cursos positions
        self.left.set_cursor(context, left_object)
        self.right.set_cursor(context, right_object)

        # run actions, right_object will be modified
        run_actions(context, self.actions)

        # restore old cursors
        self.left.set_cursor(context, old_left_cursor)
        self.right.set_cursor(context, old_right_cursor)

        # with old right cursor set assign new value
        self.right.set(context, right_object)


class Switch(object):
    def __init__(self, *fields):
        self.fields = fields
        self.tree = {}
        self.default_actions = None

        self.dispatch_table = []

    def case(self, switch_values, actions):
        if not isinstance(switch_values, (tuple, list)):
            raise TypeError("Switch case should be tuple or list")

        if len(switch_values) != len(self.fields):
            raise TypeError("Switch case length mismatch")

        nested_set(self.tree, switch_values, {"actions": actions})
        self.dispatch_table.append((switch_values, actions))

        return self

    def default(self, actions):
        self.default_actions = actions
        return self

    def _run(self, ctx):
        keys = []
        for field in self.fields:
            # case can not match abscent label
            if not field.has(ctx):
                return [], []
            keys.append(field.get(ctx))

        node = nested_get(self.tree, keys)
        if node:
            return keys, node["actions"]
        return [], []

    def run(self, ctx):
        _, actions = self._run(ctx)
        return actions

    def merge(self, other):
        all_eq = all(a == b for a, b in zip_longest(
            self.fields, other.fields))

        if not all_eq:
            raise ValueError("accessors are different")
        if other.default_actions is not None:
            raise ValueError("can not merge default actions")

        for values, actions in other.dispatch_table:
            self.case(values, actions)

        return self

    @classmethod
    def compile(cls, compiler, dct):
        fields_spec = dct["fields"]
        fields = [compiler.load_field(field) for field in fields_spec]

        switch = cls(*fields)
        cases_spec = dct["cases"]
        for case_spec in cases_spec:
            matches = case_spec["case"]
            rules = [compiler.load_operation(co) for co in case_spec["rules"]]
            switch.case(tuple(matches), rules)
        return switch

class Validate(object):
    def __init__(self, field, validator):
        self.field = field
        self.validator = validator

    def run(self, context):
        try:
            self.validator._validate(context, self.field)  # pylint: disable=protected-access
        except ValidationError as exc:
            context.errors.append(exc)

    @classmethod
    def compile(cls, compiler, dct):
        field = compiler.load_field(dct["field"])
        validator = compiler.load_validator(dct["validator"])
        return cls(field=field, validator=validator)

class Executor(object):
    def __init__(self, actions):
        self.actions = actions

    def run(self, context):
        run_actions(context, self.actions)


def run_actions(context, actions):
    for action in actions:
        next_actions = action.run(context)
        if next_actions is not None:
            run_actions(context, next_actions)


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
