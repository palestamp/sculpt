import unittest
import os

from sculpt.schema import Resolver, Loader


BASE_DIR = os.path.dirname(__file__)
CASES_DIR = os.path.join(BASE_DIR, "cases")


def assert_items_equal(test_case, list_1, list_2):
    test_case.assertListEqual(sorted(list_1), sorted(list_2))


class TestResolver(unittest.TestCase):
    def test_includes(self):
        sample_base = os.path.join(CASES_DIR, "includes")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")

        resolver = Resolver(loader)

        out = resolver.resolve(data)
        expect = {
            'child': {
                'region': {
                    'NY': 1
                },
                'variables': {
                    'var_0': 1,
                    'var_1': 2
                }
            },
            'child_vars': {
                'var_0': 1,
                'var_1': 2
            }
        }
        self.assertDictEqual(expect, out.variables.data)

    def test_references(self):
        sample_base = os.path.join(CASES_DIR, "references")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")

        internal_refs = {
            "counts": 123
        }
        resolver = Resolver(loader, irefs=internal_refs)

        out = resolver.resolve(data)
        expect = {
            'key_0': 1,
            'key_1': 2,
            'iref_0': 123,
        }
        self.assertDictEqual(expect, out.rules.data)

    def test_keys_and_values(self):
        sample_base = os.path.join(CASES_DIR, "kvs")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")

        resolver = Resolver(loader)

        out = resolver.resolve(data)
        d = out.rules.data
        assert_items_equal(self, d["region_keys"], ["first", "second"])
        assert_items_equal(self, d["region_values"], [1, 2])
        assert_items_equal(self, d["inplace_keys"], ["first", "second"])
        assert_items_equal(self, d["inplace_values"], [1, 2])

    def test_scoped_include(self):
        sample_base = os.path.join(CASES_DIR, "include-scope")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")

        resolver = Resolver(loader)

        out = resolver.resolve(data)

        expect = [{
            "op": "copy",
            "left": {
                "name": "parent-price",
                "type": "input"
            },
            "right": {
                "name": "parent-iprice",
                "type": "output"
            }
        }, {
            "op": "combine",
            "rules": [{
                "op": "copy",
                "left": {
                    "type": "input",
                    "name": "child-price"
                },
                "right": {
                    "type": "output",
                    "name": None
                },
                "wigth": 40
            }]
        }, {
            "op": "copy",
            "wigth": 10
        }]
        self.assertListEqual(expect, out.rules.data)

    def test_fn(self):
        sample_base = os.path.join(CASES_DIR, "fn")
        loader = Loader(sample_base)
        data = loader.load_file("parent.yml")


        resolver = Resolver(loader)

        out = resolver.resolve(data)

        expect = [{
            "op": "combine",
            "ops": [{
                "op": "copy",
                "left": {
                    "type": "input",
                    "name": "region"
                },
                "right": {
                    "type": "output",
                    "name": "region"
                }
            }]
        }, {
            "op": "copy",
            "left": {
                "type": "input",
                "name": "name"
            },
            "right": {
                "type": "output",
                "name": "name"
            }
        }]
        self.assertEqual(expect, out.rules.data)
