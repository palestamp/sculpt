import sys

import yaml


class Tag(yaml.YAMLObject):
    pass

class NestedTag(Tag):
    def delegate(self, func, scope):
        raise NotImplementedError
