class KeysResolver(object):
    def resolve(self, _resolver, tag):
        try:
            return list(tag.obj.keys())
        except Exception as _:
            raise Exception("can not get keys", tag.obj, lineno=tag.__lineno__)

    def resolve_values(self, obj, node):
        try:
            return list(obj.values())
        except Exception as _:
            raise BadKeys("can not get values", obj, lineno=tag.__lineno__)
