import os
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import yaml

from ..util import nested_get


class IncludeResolver(object):
    def resolve(self, root_resolver, url):
        data = self.load(root_resolver, url)
        return root_resolver.resolve_dict(data)

    def load(self, root_resolver, url):
        if url.scheme == "file":
            return self.from_file(root_resolver, url)
        elif url.scheme == "s3":
            return self.from_s3(root_resolver, url)
        else:
            raise Exception("unrecognized scheme: '{}'".format(url.scheme))

    def from_file(self, root_resolver, url):
        path = url.path.lstrip("/")
        path = os.path.join(root_resolver.loader.root_dir, url.netloc, path)
        path = path.rstrip("/")

        with open(path) as source:
            data = root_resolver.loader.load(source)
            if url.fragment != '':
                data = nested_get(data, url.fragment.split('.'))

            return data

    def from_s3(self, _root_resolver, url):
        raise NotImplementedError


class Include(yaml.YAMLObject):
    yaml_tag = u'!include'
    resolver = IncludeResolver()

    def __init__(self, uri):
        self.uri = urlparse(uri)

    def __repr__(self):
        return 'Include({})'.format(self.uri)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.uri)

    def resolve(self, resolver, _scope):
        return self.resolver.resolve(resolver, self.uri)


class IncludeRulesResolver(IncludeResolver):
    def resolve(self, root_resolver, url):
        if url.fragment != '':
            raise Exception("fragment is forbidden in scoped include")
        data = super(IncludeRulesResolver, self).load(root_resolver, url)
        scope = root_resolver.resolve(data)
        return scope.rules.data


class IncludeRules(yaml.YAMLObject):
    yaml_tag = u'!include-rules'
    resolver = IncludeRulesResolver()

    def __init__(self, uri):
        self.uri = urlparse(uri)

    def __repr__(self):
        return 'IncludeRules({})'.format(self.uri)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.uri)

    def resolve(self, resolver, _scope):
        return self.resolver.resolve(resolver, self.uri)
