from functools import reduce
from operator import getitem


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
    def __init__(self, actions):
        self.actions = actions

    def run(self, context):
        run_actions(context, self.actions)


def run_actions(context, actions):
    for action in actions:
        next_actions = action.run(context)
        if next_actions is not None:
            run_actions(context, next_actions)
