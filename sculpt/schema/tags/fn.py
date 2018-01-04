
from .tag import NestedTag


class Fn(NestedTag):
    yaml_tag = u'!fn'

    def __init__(self, ref, defs):
        self.ref = ref
        self.defs = defs

    @classmethod
    def from_yaml(cls, loader, node):
        mapping = loader.construct_mapping(node, deep=True)
        ref = mapping["ref"]
        defs = mapping.get("defs", [])
        return cls(ref, defs)

    def delegate(self, func, scope):
        def _recur(node, func):
            if isinstance(node, dict):
                return {k: _recur(v, func) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func) for v in node]
            elif isinstance(node, NestedTag):
                node = node.delegate(func, scope)
            return func(node, scope)

        self.defs = _recur(self.defs, func)
        return self

    def __repr__(self):
        return 'Fn({}, {})'.format(self.ref, self.defs)
