import yaml
import yaml.nodes

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
        if not dereferenced:
            raise cls.exc_type("expected 'map' key inside",
                               node, lineno=node.__lineno__)

        return cls(dereferenced, lineno=node.__lineno__)

    def delegate(self, func, scope):
        self.obj = func(self.obj, scope)
        return self


class BadKeys(TagError):
    def __str__(self):
        return 'Bad keys, {}: !keys {}, at line:{}'.format(self.args[0], self.args[1], self.lineno)


class Keys(KVViewTag):
    yaml_tag = u'!keys'
    exc_type = BadKeys

    def __init__(self, obj, lineno=None):
        self.obj = obj
        self.__lineno__ = lineno

    def __repr__(self):
        return 'Keys({})'.format(self.obj)
