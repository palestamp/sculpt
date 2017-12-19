import unittest

from sculpt.core import Context, Output, Input, Copy, Executor
from sculpt.validation import Validate, NotEmptyValidator


class TestValidation(unittest.TestCase):
    def test_not_empty(self):
        context = Context({
            "name": "Python"
        })

        executor = Executor([
            Copy(Input("name"), Output("name")),
            Validate(Output("nam"), NotEmptyValidator())
        ])

        executor.run(context)

        error_kwargs = context.errors[0].kwargs
        expect = {
            "section": Output.section,
            "label": "nam"
        }

        self.assertDictEqual(expect, error_kwargs)
        