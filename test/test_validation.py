import unittest

from sculpt.core import Context, Output, Input, Copy, Executor
from sculpt.validation import Validate, NotEmptyValidator, InValidator


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
            Validate(Input("age"), InValidator([1, 2, 3, 4, 5]))
        ])

        executor.run(context)
        expect = "input:age field does not belong to requested values"
        self.assertEqual(expect, context.errors[0].message)

