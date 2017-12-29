import os

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from ..util import nested_get


class IncludeResolver(object):
    def resolve(self, root_resolver, tag):
        url = urlparse(tag.url)
        
        data = self.load(root_resolver, url)
        return root_resolver.resolve_dict(data)

    def load(self, root_resolver, url):
        if url.scheme == "file":
            return self.from_file(root_resolver, url)
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
