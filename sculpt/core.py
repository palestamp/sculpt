from functools import reduce
from operator import getitem


class Storage(object):
    section = None

    def __init__(self, label):
        self.label = label

    def get_cursor(self, context):
        return context.cursors[self.section]

    def set_cursor(self, context, item):
        context.cursors[self.section] = item

    def __eq__(self, other):
        return (self.section == other.section and self.label == other.label)


class Input(Storage):
    section = "input"

    def get(self, context):
        return nested_get(context.cursors[self.section], split_label(self.label))

    def has(self, context):
        return nested_has(context.cursors[self.section], split_label(self.label))

    def set(self, context, value):
        raise ValueError("set operation not allowed on Input")


class Output(Storage):
    section = "output"

    def get(self, context):
        return nested_get(context.cursors[self.section], split_label(self.label))
    
    def has(self, context):
        return nested_has(context.cursors[self.section], split_label(self.label))

    def set(self, context, value):
        nested_set(context.cursors[self.section], split_label(self.label), value)


class Context(object):
    def __init__(self, _input):
        self.stores = {
            Input.section: _input,
            Output.section: {}
        }

        self.cursors = {
            Input.section: self.stores[Input.section],
            Output.section: self.stores[Output.section]
        }

        self.errors = []


class Copy(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def run(self, context):
        value = self.left.get(context)

        # ignore field if it not exists
        if value is None and not self.left.has(context):
            return

        self.right.set(context, value)


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


class Executor(object):
    def __init__(self, actions):
        self.actions = actions

    def run(self, context):
        run_actions(context, self.actions)


def run_actions(context, actions):
    for action in actions:
        action.run(context)


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


def nested_set(dct, keys, value):
    leaf = reduce(lambda d, k: d.setdefault(k, {}), keys[:-1], dct)
    leaf[keys[-1]] = value


def split_label(label):
    return label.split(".")
