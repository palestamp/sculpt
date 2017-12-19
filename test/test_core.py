import unittest

from sculpt.core import *


class TestSome(unittest.TestCase):
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
        
        self.assertDictEqual(output, context.stores[Output._type])

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
                Copy(Output("c"), Output("signed.count"))
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

        self.assertDictEqual(output, context.stores[Output._type])

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
                    Copy(Output("c"), Output("signed.count"))
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

        self.assertDictEqual(output, context.stores[Output._type])
