from sculpt.compat import isstr
from sculpt.fields import Input, Output, VirtualVar
from sculpt.actions import Copy, Switch, Combine, Validate, Apply, Delete
from sculpt.validation import InSetValidator, NotEmptyValidator


DEFAULT_FIELDS = {
    "input": Input,
    "output": Output,
    "virtual_var": VirtualVar,
}


DEFAULT_ACTIONS = {
    "validate": Validate,
    "switch": Switch,
    "copy": Copy,
    "combine": Combine,
    "apply": Apply,
    "delete": Delete,
}


DEFAULT_VALIDATORS = {
    "InSet": InSetValidator,
    "NotEmpty": NotEmptyValidator
}


class Compiler(object):
    def __init__(self, fields=None, actions=None, validators=None):
        self.actions = DEFAULT_ACTIONS.copy()
        self.fields = DEFAULT_FIELDS.copy()
        self.validators = DEFAULT_VALIDATORS.copy()

        self.actions.update(actions or {})
        self.fields.update(fields or {})
        self.validators.update(validators or {})

    def compile(self, rules):
        return [self.load_operation(op) for op in rules]

    def load_operation(self, op_spec):
        operation = op_spec["op"]
        try:
            cls = self.actions[operation]
        except KeyError:
            raise Exception("unknown operation: {}".format(operation))
        return cls.compile(self, op_spec)

    def load_field(self, field_spec):
        field_type = field_spec["type"]
        cls = self.fields[field_type]
        return cls.compile(self, field_spec)

    def load_validator(self, validator_spec):
        if isstr(validator_spec):
            cls = self.validators[validator_spec]
            return cls()

        validator_type = validator_spec["type"]
        parameters = validator_spec.get("args", {})
        cls = self.validators[validator_type]
        return cls(**parameters)
