from __future__ import absolute_import
import unittest

from sculpt.core import Context, Executor, Schema
from sculpt.operations import Copy, Each, With, Validate, Combine, Delete, Switch
from sculpt.fields import Input, Output, VirtualVar, VirtualList, Virtual
from sculpt.ast import EvictNestedCombines

class TestElement(unittest.TestCase):
    def test_eq(self):
        a = Copy(Input("a"), Output("b"))
        b = Copy(Input("a"), Output("b"))
        c = Copy(Input("v"), Output("b"))

        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)


class TestCopy(unittest.TestCase):
    def test_copy(self):
        context = Context({
            "person": {
                "name": "Aaron"
            }
        })

        executor = Executor([
            Copy(Input("person"), Output("personality")),
            Copy(Input("person.name"), Output("name")),
            Copy(Output("name"), Output("name_1"))
        ])

        executor.run(context)

        output = {
            'name_1': 'Aaron',
            'name': 'Aaron',
            'personality': {
                'name': 'Aaron'
            }
        }

        self.assertDictEqual(output, context.stores[Output.section])

    def test_copy_ignore_non_existent_field(self):
        context = Context({
            "person": {
                "name": "Aaron"
            }
        })

        executor = Executor([
            Copy(Input("age"), Output("age")),
            Copy(Input("person.name"), Output("name")),
            Copy(Output("name"), Output("name_1"))
        ])

        executor.run(context)

        output = {
            'name_1': 'Aaron',
            'name': 'Aaron',
        }
        self.assertDictEqual(output, context.stores[Output.section])

    def test_input_raises_on_assing_at_init_time(self):
        with self.assertRaisesRegexp(ValueError, "set operation not allowed on Input"):
            Executor([
                Copy(Input("age"), Input("age_2")),
            ])


class TestModifiers(unittest.TestCase):
    def test_combine(self):
        context = Context({
            "person": {
                "name": "Aaron",
                "age": 56
            }
        })

        combination = Combine(
            Copy(Input("person.age"), Output("age")),
            Copy(Input("person.name"), Output("name"))
        )

        executor = Executor([
            combination,
            Copy(Output("name"), Output("name_1"))
        ])

        executor.run(context)

        output = {
            'name_1': 'Aaron',
            'name': 'Aaron',
            'age': 56,
        }

        self.assertDictEqual(output, context.stores[Output.section])

    def test_each(self):
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
            Each(Input("items"), Output("counts"), [
                Copy(Input("year"), Output("y")),
                Copy(Input("count"), Output("c")),
                Copy(Output("c"), Output("signed.count")),
                Copy(Output("c"), VirtualList("avg.count").append())
            ])
        ])

        executor.run(context)

        output = {
            "counts": [{
                "y": 1987,
                "c": 145,
                "signed": {
                    "count": 145
                }
            }, {
                "y": 1992,
                "c": 178,
                "signed": {
                    "count": 178
                }
            }]
        }

        virtual = {
            'avg.count': [145, 178]
        }
        self.assertDictEqual(virtual, context.stores[Virtual.section])
        self.assertDictEqual(output, context.stores[Output.section])

    def test_with(self):
        context = Context({
            "event": {
                "object": {
                    "items": [{
                        "year": 1987,
                        "count": 145
                    }, {
                        "year": 1992,
                        "count": 178
                    }]
                }
            }
        })

        executor = Executor([
            With(Input("event.object"), Output("data.output"), [
                Each(Input("items"), Output("counts"), [
                    Copy(Input("year"), Output("y")),
                    Copy(Input("count"), Output("c")),
                    Copy(Output("c"), Output("signed.count")),
                ])
            ])
        ])

        executor.run(context)

        output = {
            "data": {
                "output": {
                    "counts": [{
                        "y": 1987,
                        "c": 145,
                        "signed": {
                            "count": 145
                        }
                    }, {
                        "y": 1992,
                        "c": 178,
                        "signed": {
                            "count": 178
                        }
                    }]
                }
            }
        }

        self.assertDictEqual(output, context.stores[Output.section])

    def test_inplace_list_unwrap(self):
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
            Each(Input("items"), Output("years"), [
                Copy(Input("year"), VirtualList("tmp.years").append()),
            ]),
            Copy(VirtualList("tmp.years"), Output("years")),
            Delete(VirtualList("tmp.years"))
        ])

        executor.run(context)

        output = {
            "years": [1987, 1992]
        }
        virtual = {}
        self.assertDictEqual(virtual, context.stores[Virtual.section])
        self.assertDictEqual(output, context.stores[Output.section])


class TestSwitch(unittest.TestCase):
    def test_switch_case(self):
        context = Context({
            "category": "cars",
            "wheel": 12,
            "weight": 1765
        })

        executor = Executor([
            Copy(Input("category"), Output("category")),
            (
                Switch(Input("category"))
                .case(["cars"], [
                    Copy(Input("wheel"), Output("wheel")),
                    Copy(Input("weight"), VirtualVar("avg.weight"))
                ])
                .case(["real_estate"], [
                    Copy(Input("address"), Output("address"))
                ])
                .default([])
            )
        ])

        executor.run(context)

        output = {
            'category': 'cars',
            'wheel': 12
        }

        virtual = {
            "avg.weight": 1765
        }
        self.assertDictEqual(output, context.stores[Output.section])
        self.assertDictEqual(virtual, context.stores[Virtual.section])

    def test_switch_merge(self):
        context = Context({
            "category": "cars",
            "wheel": 12,
            "weight": 1765
        })

        cars_branch = (
            Switch(Input("category"))
            .case(["cars"], [
                Copy(Input("wheel"), Output("wheel")),
            ])
        )

        real_estate_branch = (
            Switch(Input("category"))
            .case(["real_estate"], [
                Copy(Input("address"), Output("address")),
            ])
        )

        main_case = (
            Switch(Input("category"))
            .merge(cars_branch)
            .merge(real_estate_branch)
            .default([])
        )

        executor = Executor([
            Copy(Input("category"), Output("category")),
            main_case
        ])

        executor.run(context)

        output = {
            'category': 'cars',
            'wheel': 12
        }
        self.assertDictEqual(output, context.stores[Output.section])

    def test_switch_merge_different(self):
        cars_branch = (
            Switch(Input("category"), Input("wheel"))
            .case(["cars", 12], [
                Copy(Input("wheel"), Output("wheel")),
            ])
        )

        real_estate_branch = (
            Switch(Input("category"), Output("wheel"))
            .case(["real_estate", 12], [
                Copy(Input("address"), Output("address")),
            ])
        )

        with self.assertRaises(ValueError):
            (
                Switch(Input("category"))
                .merge(cars_branch)
                .merge(real_estate_branch)
                .default([])
            )

    def test_switch_no_fields(self):
        context = Context({
            "category": "cars",
            "wheel": 12,
            "weight": 1765
        })

        cars_branch = (
            Switch(Input("category"), Input("type"))
            .case(["cars", "sell"], [
                Copy(Input("wheel"), Output("wheel")),
            ])
        )

        real_estate_branch = (
            Switch(Input("category"), Input("type"))
            .case(["real_estate", "sell"], [
                Copy(Input("address"), Output("address")),
            ])
        )

        main_case = (
            Switch(Input("category"), Input("type"))
            .merge(cars_branch)
            .merge(real_estate_branch)
            .default([])
        )

        executor = Executor([
            main_case
        ])

        executor.run(context)

        self.assertDictEqual({}, context.stores[Output.section])
