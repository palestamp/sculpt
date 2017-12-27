import yaml

from .delegate import Delegate
from sculpt.compat import isstr

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

        def _recur(d, func):
            if isinstance(d, dict):
                return {k: _recur(v, func) for k, v in d.items()}
            elif isinstance(d, list):
                return [_recur(v, func) for v in d]
            return func(d)

        def subs(vk):
            is_var, k = self.variable(vk)
            if is_var:
                if k in allowed:
                    return defines[k]
            return vk

        return _recur(fnbody, subs)

    @staticmethod
    def variable(s):
        if not isstr(s):
            return False, ""

        if s and s[0] == '$':
            return True, s[1:]
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
