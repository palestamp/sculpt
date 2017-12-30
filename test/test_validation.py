import unittest

from sculpt.core import Context, Executor
from sculpt.fields import Input, Output
from sculpt.actions import Copy, Validate
from sculpt.validation import NotEmptyValidator, InSetValidator


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

    def test_in_validator(self):
        context = Context({
            "age": 38
        })

        executor = Executor([
            Validate(Input("age"), InSetValidator([1, 2, 3, 4, 5]))
        ])

        executor.run(context)
        expect = "input:age field does not belong to requested values"
        self.assertEqual(expect, str(context.errors[0]))

