import sys
import abc

import yaml

if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})


class Tag(ABC, yaml.YAMLObject):
    @abc.abstractproperty
    def yaml_tag(self):
        pass

    @abc.abstractmethod
    def from_yaml(cls, loader, node):
        pass


class NestedTag(Tag):
    @abc.abstractmethod
    def delegate(self, func, scope):
        pass
