
class IRefResolver(object):
    def resolve(self, resolver, _scope, tag):
        found, iref = resolver.lookup_iref(tag.ref)
        if not found:
            raise Exception("iref '{}' not found".format(tag.ref))
        return iref
