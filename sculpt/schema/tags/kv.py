import yaml
import yaml.nodes

from .ref import Ref, IRef
from .exceptions import TagError
from .tag import NestedTag

class KVViewTag(NestedTag):
    obj = None
    exc_type = Exception

    @classmethod
    def from_yaml(cls, loader, node):
        if not isinstance(node, yaml.nodes.MappingNode):
            raise cls.exc_type("expected MappingNode",
                               node, lineno=node.__lineno__)

        mapping = loader.construct_mapping(node, deep=True)

        dereferenced = mapping.get('map')
        if not isinstance(dereferenced, (Ref, IRef, dict)):
            raise cls.exc_type("expected 'map' key inside",
                               node, lineno=node.__lineno__)

        return cls(dereferenced, lineno=node.__lineno__)

    def delegate(self, func, scope):
        self.obj = func(self.obj, scope)
        return self


class BadKeys(TagError):
    def __str__(self):
        return 'Bad keys, {}: !keys {}, at line:{}'.format(self.args[0], self.args[1], self.lineno)


class KVResolver(object):
    def resolve_keys(self, obj, node):
        try:
            return list(obj.keys())
        except Exception as _:
            raise BadKeys("can not get keys", obj, lineno=node.__lineno__)

    def resolve_values(self, obj, node):
        try:
            return list(obj.values())
        except Exception as _:
            raise BadKeys("can not get values", obj, lineno=node.__lineno__)


class Keys(KVViewTag):
    yaml_tag = u'!keys'
    exc_type = BadKeys
    resolver = KVResolver()

    def __init__(self, obj, lineno=None):
        self.obj = obj
        self.__lineno__ = lineno

    def __repr__(self):
        return 'Keys({})'.format(self.obj)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.obj)

    def resolve(self, _resolver, _scope):
        return self.resolver.resolve_keys(self.obj, self)


class BadValues(TagError):
    def __str__(self):
        return 'Bad values, {}: !values {}, at line:{}'.format(
            self.args[0], self.args[1], self.lineno)


class Values(KVViewTag):
    yaml_tag = u'!values'
    exc_type = BadValues
    resolver = KVResolver()

    def __init__(self, obj, lineno=None):
        self.obj = obj
        self.__lineno__ = lineno

    def __repr__(self):
        return 'Values({})'.format(self.obj)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.obj)

    def resolve(self, _resolver, _scope):
        return self.resolver.resolve_values(self.obj, self)
