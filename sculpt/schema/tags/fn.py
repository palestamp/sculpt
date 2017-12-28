import yaml

from sculpt.compat import isstr
from .delegate import Delegate


class FnResolver(object):
    def resolve(self, _resolver, scope, ref, defs):
        found, fnbody = scope.lookup_function(ref)
        if not found:
            raise Exception("function '{}' not found".format(ref))

        compiled = self.resolve_defines(defs, fnbody)
        return {
            "op": "combine",
            "ops": compiled["rules"]
        }

    def resolve_defines(self, defines, fnbody):
        allowed = fnbody.get('define', [])

        def _recur(node, func):
            if isinstance(node, dict):
                return {k: _recur(v, func) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func) for v in node]
            return func(node)

        def subs(node):
            is_var, name = self.variable(node)
            if is_var:
                if name in allowed:
                    return defines[name]
            return node

        return _recur(fnbody, subs)

    @staticmethod
    def variable(node):
        if not isstr(node):
            return False, ""

        if node and node[0] == '$':
            return True, node[1:]
        return False, ""


class Fn(yaml.YAMLObject, Delegate):
    yaml_tag = u'!fn'
    resolver = FnResolver()

    def __init__(self, ref, defs):
        self.ref = ref
        self.defs = defs

    def __repr__(self):
        return 'Fn({}, {})'.format(self.ref, self.defs)

    @classmethod
    def from_yaml(cls, loader, node):
        mapping = loader.construct_mapping(node, deep=True)
        ref = mapping["ref"]
        defs = mapping["defs"]
        return cls(ref, defs)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.uri)

    def resolve(self, resolver, scope):
        return self.resolver.resolve(resolver, scope, self.ref, self.defs)

    def delegate(self, func, scope):
        def _recur(node, func):
            if isinstance(node, dict):
                return {k: _recur(v, func) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func) for v in node]
            elif isinstance(node, Delegate):
                node = node.delegate(func, scope)
            return func(node, scope)

        self.defs = _recur(self.defs, func)
        return self
