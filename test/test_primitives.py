import unittest

from sculpt.primitives import FieldSelect
from sculpt.core import Executor, Context, Input, Output



class TestFieldSelect(unittest.TestCase):
    def test_field_select(self):
        context = Context({
            "items": [{
                "year": 1987,
                "count": 145
            }, {
                "year": 1992,
                "count": 178
            }]
        })

        executor = Executor([
            FieldSelect(Input("items"), "year", Output("years")),
            FieldSelect(Input("items"), "count", Output("counts"))
        ])

        executor.run(context)

        output = {
            'years': [1987, 1992],
            'counts': [145, 178],
        }
        self.assertDictEqual(output, context.stores[Output.section])
