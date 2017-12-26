
import yaml

from ..util import nested_get

class RefResolver(object):
    def resolve(self, _resolver, scope, ref):
        return scope.lookup_variable(ref)


class Ref(yaml.YAMLObject):
    yaml_tag = u'!ref'
    resolver = RefResolver()

    def __init__(self, ref):
        self.ref = ref

    def __repr__(self):
        return 'Ref({})'.format(self.ref)

    @classmethod
    def from_yaml(cls, loader, node):
        return Ref(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.ref)

    def resolve(self, resolver, scope):
        return self.resolver.resolve(resolver, scope, self.ref)


class IRefResolver(object):
    def resolve(self, resolver, _scope, ref):
        return resolver.lookup_iref(ref)


class IRef(yaml.YAMLObject):
    yaml_tag = u'!iref'
    resolver = IRefResolver()

    def __init__(self, ref):
        self.ref = ref

    def __repr__(self):
        return 'IRef({})'.format(self.ref)

    @classmethod
    def from_yaml(cls, loader, node):
        return IRef(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.ref)

    def resolve(self, resolver, scope):
        return self.resolver.resolve(resolver, scope, self.ref)
