from .validation import ValidationError
from .fields import Input, Output, Virtual


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


class Executor(object):
    def __init__(self, operations):
        self.operations = operations

    def run(self, context):
        execute_operations(context, self.operations)


def execute_operations(context, operations):
    for operation in operations:
        next_operations = operation.run(context)
        if next_operations is not None:
            execute_operations(context, next_operations)
