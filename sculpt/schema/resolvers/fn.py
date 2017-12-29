from sculpt.compat import isstr


class FnResolver(object):
    def resolve(self, _resolver, scope, tag):

        found, fnbody = scope.lookup_function(tag.ref)
        if not found:
            raise Exception("function '{}' not found".format(tag.ref))

        compiled = self.resolve_defines(tag.ref, tag.defs, fnbody)
        return {
            "op": "combine",
            "ops": compiled["rules"]
        }

    def resolve_defines(self, ref, defines, fnbody):
        allowed = fnbody.get('define', [])

        def _recur(node, func):
            if isinstance(node, dict):
                return {k: _recur(v, func) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func) for v in node]
            return func(node)

        def subs(node):
            is_var, name = parse_variable(node)
            if is_var:
                if name not in allowed:
                    raise Exception("unknown var '{}' in function '{}'".format(name, ref))
                if name in allowed:
                    return defines.get(name)
            return node

        return _recur(fnbody, subs)


def parse_variable(node):
    if not isstr(node):
        return False, ""

    if node and node[0] == '$':
        return True, node[1:]
    return False, ""
