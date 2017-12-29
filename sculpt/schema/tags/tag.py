import sys
import abc

import yaml

if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})


class Tag(yaml.YAMLObject):
    pass

class NestedTag(Tag):
    def delegate(self, func, scope):
        raise NotImplementedError
