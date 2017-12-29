from .include import IncludeResolver, urlparse


class IncludeRulesResolver(IncludeResolver):
    def resolve(self, root_resolver, tag):
        url = urlparse(tag.url)

        if url.fragment != '':
            raise Exception("fragment is forbidden in scoped include")
        data = super(IncludeRulesResolver, self).load(root_resolver, tag)
        scope = root_resolver.resolve(data)
        return scope.rules.data
