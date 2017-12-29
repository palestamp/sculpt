from .include import IncludeResolver, urlparse


class IncludeRulesResolver(IncludeResolver):
    def resolve(self, resolver, scope, tag):
        url = urlparse(tag.url)

        if url.fragment != '':
            raise Exception("fragment is forbidden in scoped include")
        data = super(IncludeRulesResolver, self).load(resolver, url)
        scope = resolver.resolve(data)
        return scope.rules.data
