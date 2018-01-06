import collections

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


class Schema(object):
    def __init__(self, operations):
        self.operations = operations

    def accept(self, visitor):
        visitor.visit_schema(self)

    def __repr__(self):
        ops = ", ".join(str(op) for op in self.operations)
        return "Schema({})".format(ops)


class Executor(object):
    def __init__(self, schema):
        self.root = None
        if isinstance(schema, Schema):
            self.root = schema
        elif isinstance(schema, collections.MutableSequence):
            self.root = Schema(schema)
        else:
            raise ValueError(
                "executor accepts list of operations or Schema, got: {}".format(
                    type(schema))
            )

    def run(self, context):
        execute_operations(context, self.root.operations)
        return context


def execute_operations(context, operations):
    for operation in operations:
        next_operations = operation.run(context)
        if next_operations is not None:
            execute_operations(context, next_operations)
