
class RefResolver(object):
    def resolve(self, _resolver, scope, tag):
        found, var = scope.lookup_variable(tag.ref)
        if not found:
            raise Exception("ref '{}' not found".format(tag.ref))
        return var


class RefValuesResolver(RefResolver):
    def resolve(self, _resolver, scope, tag):
        value = super(RefValuesResolver, self).resolve(_resolver, scope, tag)
        try:
            return list(value.values())
        except Exception as e:
            raise Exception("can not get values from ref-values '{}'".format(tag.ref))
