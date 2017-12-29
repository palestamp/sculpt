
class ValuesResolver(object):
    def resolve(self, _resolver, tag):
        try:
            return list(tag.obj.values())
        except Exception as _:
            raise Exception("can not get values", tag.obj, lineno=tag.__lineno__)
