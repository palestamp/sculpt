
import yaml




class Ref(yaml.YAMLObject):
    yaml_tag = u'!ref'

    def __init__(self, ref):
        self.ref = ref

    @classmethod
    def from_yaml(cls, loader, node):
        return Ref(node.value)

    def __repr__(self):
        return 'Ref({})'.format(self.ref)


class RefValues(Ref):
    yaml_tag = u'!ref-values'

    @classmethod
    def from_yaml(cls, loader, node):
        return RefValues(node.value)

    def __repr__(self):
        return 'RefValues({})'.format(self.ref)
