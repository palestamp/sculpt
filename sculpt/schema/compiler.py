
from sculpt.core import (
    Copy, Switch, Input, Output,
    VirtualVar, Combine, Validate, Apply, Delete
)

from sculpt.validation import InSetValidator, NotEmptyValidator

class Compiler(object):
    fields = {
        "input": Input,
        "output": Output,
        "virtual_var": VirtualVar,
    }

    actions = {
        "validate": Validate,
        "switch": Switch,
        "copy": Copy,
        "combine": Combine,
        "apply": Apply,
        "delete": Delete,
    }

    validators = {
        "InSet": InSetValidator,
        "NotEmpty": NotEmptyValidator
    }

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
        validator_type = validator_spec["type"]
        parameters = validator_spec.get("args", {})
        cls = self.validators[validator_type]
        return cls(**parameters)
