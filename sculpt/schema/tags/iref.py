from .tag import Tag


class IRef(Tag):
    yaml_tag = u'!iref'

    def __init__(self, ref):
        self.ref = ref

    @classmethod
    def from_yaml(cls, loader, node):
        return IRef(node.value)

    def __repr__(self):
        return 'IRef({})'.format(self.ref)
