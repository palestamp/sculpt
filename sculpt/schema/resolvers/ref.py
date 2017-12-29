
class RefResolver(object):
    def resolve(self, _resolver, scope, tag):
        found, var = scope.lookup_variable(tag.ref)
        if not found:
            raise Exception("ref '{}' not found".format(tag.ref))
        return var
