import os

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from ..util import nested_get


class IncludeResolver(object):
    def resolve(self, resolver, _scope, tag):
        url = urlparse(tag.url)

        data = self.load(resolver, url)
        return resolver.resolve_dict(data)

    def load(self, resolver, url):
        if url.scheme == "file":
            return self.from_file(resolver, url)
        else:
            raise Exception("unrecognized scheme: '{}'".format(url.scheme))

    def from_file(self, resolver, url):
        path = url.path.lstrip("/")
        path = os.path.join(resolver.loader.root_dir, url.netloc, path)
        path = path.rstrip("/")

        with open(path) as source:
            data = resolver.loader.load(source)
            if url.fragment != '':
                data = nested_get(data, url.fragment.split('.'))

            return data
