import os
import unittest

from sculpt.schema import Resolver, Loader
from sculpt.schema.compiler import Compiler


BASE_DIR = os.path.dirname(__file__)
CASES_DIR = os.path.join(BASE_DIR, "cases")


class TestCompiler(unittest.TestCase):
    def test_compiler(self):
        sample_base = os.path.join(CASES_DIR, "compiler")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")

        irefs = {
            "get_parent_category": get_parent_category
        }
        resolver = Resolver(loader, irefs=irefs)

        out = resolver.resolve(data)
        compiler = Compiler()

        from sculpt.core import Executor, Context
        schema = compiler.compile(out.rules.data)
        executor = Executor(schema)

        context = Context({
            "region": 1,
            "category": 12234,
            "area": 2,
            "12000_key" : 12000,
            "1000_key" : 1000,
            "default_key": "default"
        })

        executor.run(context)

        expected_output = {
            'category': 12234,
            'region': 1,
            'area': 2,
            'parent_category_final': 12000,
            '12000_key': 12000,
        }

        self.assertDictEqual(expected_output, context.stores["output"])
        self.assertEqual(0, len(context.errors))


def get_parent_category(value):
    int_val = int(value)
    return int_val // 1000 * 1000
