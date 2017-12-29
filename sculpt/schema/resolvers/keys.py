
class KeysResolver(object):
    def resolve(self, _resolver, _scope, tag):
        try:
            return list(tag.obj.keys())
        except Exception as _:
            raise Exception("can not get keys", tag.obj, lineno=tag.__lineno__)
