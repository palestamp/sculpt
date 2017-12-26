import yaml
from yaml.composer import Composer
from yaml.constructor import Constructor

from .util import InfoDict


def register_tag(tag_cls):
    yaml.SafeLoader.add_constructor(tag_cls.yaml_tag, tag_cls.from_yaml)
    yaml.SafeDumper.add_multi_representer(tag_cls, tag_cls.to_yaml)


def composer_with_lineno(loader):
    def compose_node(parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = loader.line
        node = Composer.compose_node(loader, parent, index)
        node.__lineno__ = line + 1
        return node
    return compose_node


def constructor_with_lineno(loader):
    def construct_mapping(node, deep=False):
        mapping = Constructor.construct_mapping(loader, node, deep=deep)
        mapping = InfoDict(mapping)
        mapping.lineno = node.__lineno__
        return mapping
    return construct_mapping


def get_loader(data):
    loader = yaml.Loader(data)
    loader.compose_node = composer_with_lineno(loader)
    loader.construct_mapping = constructor_with_lineno(loader)
    return loader

