from .fields import Input
from .core import run_actions
from .util import nested_set, nested_get, zip_longest
from .validation import ValidationError
from .element import Element

class Action(Element):
    pass


class Copy(Action):
    __el_name__ = "copy"

    def __init__(self, left, right):
        self.left = left
        self.right = right

        # static check for Input assignment
        if isinstance(self.right, Input):
            # just trigger Input.set which should raise
            # XXX: strange decision, better do it as final tree validation visitor
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


class ApplyError(Exception):
    def __init__(self, message, field, function, orig_exc):
        super(ApplyError, self).__init__(message)
        self.field = field
        self.function = function
        self.orig_exc = orig_exc

    def __str__(self):
        return "{}, {}, {}".format(self.field, self.function, self.orig_exc)


class Apply(Action):
    __el_name__ = "apply"

    def __init__(self, field, function):
        self.field = field
        self.function = function

    def run(self, context):
        value = self.field.get(context)
        try:
            value = self.function(value)
        except Exception as e:
            raise ApplyError("apply error in {}".format(self.field.label),
                             self.field, self.function, e)

        self.field.set(context, value)

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


class Combine(Action):
    __el_name__ = "combine"

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
        actions = ", ".join([str(op) for op in self.actions])
        return "Combine({})".format(actions)


class Delete(Action):
    __el_name__ = "delete"

    def __init__(self, field):
        self.field = field

    def run(self, context):
        self.field.delete(context)

    @classmethod
    def compile(cls, compiler, dct):
        field = compiler.load_field(dct["field"])
        return cls(field=field)

    def __repr__(self):
        return "Delete({})".format(self.field)


class Each(Action):
    __el_name__ = "each"

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


class With(Action):
    __el_name__ = "with"

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


class Switch(Action):
    __el_name__ = "switch"

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

        default = dct.get("default")
        if default:
            rules = [compiler.load_operation(co) for co in default]
            switch.default(rules)
        return switch


class Validate(Action):
    __el_name__ = "validate"

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
