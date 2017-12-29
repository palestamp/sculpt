
import yaml


class RefResolver(object):
    def resolve(self, _resolver, scope, ref):
        found, var = scope.lookup_variable(ref)
        if not found:
            raise Exception("ref '{}' not found".format(ref))
        return var


class Ref(yaml.YAMLObject):
    yaml_tag = u'!ref'

    def __init__(self, ref):
        self.ref = ref

    @classmethod
    def from_yaml(cls, loader, node):
        return Ref(node.value)

    def __repr__(self):
        return 'Ref({})'.format(self.ref)