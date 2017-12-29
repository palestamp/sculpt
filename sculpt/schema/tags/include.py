from .tag import Tag


class Include(Tag):
    yaml_tag = u'!include'

    def __init__(self, url):
        self.url = url

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)

    def __repr__(self):
        return 'Include({})'.format(self.url)
