import os

from .tags import Delegate, Include, Ref, IRef, Keys, Values, IncludeRules
from .tags import SCULPT_TAGS
from .yml import get_loader
from .util import nested_get


class ResolutionError(Exception):
    def __init__(self, *args):
        super(ResolutionError, self).__init__(self, *args)
        self.msg = args[0]
        self.node = args[1]
        self.orig_exc = args[2]

    def __str__(self):
        return "failed to resolve {} on line: {}, ({})".format(
            self.msg, self.node.__lineno__, self.orig_exc)


class Section(dict):
    def __init__(self, data, name=None, allowed_tags=None):
        self.data = data
        self.name = name
        self.allowed_tags = tuple(allowed_tags) if allowed_tags else None

    def resolve(self, resolver, scope=None):
        res = resolver.resolve_dict(
            data=self.data,
            scope=scope,
            allowed_tags=self.allowed_tags,
            section_name=self.name)

        return Section(
            data=res,
            allowed_tags=self.allowed_tags,
            name=self.name
        )


class Scope(object):
    id_key = "id"
    variables_key = "variables"
    functions_key = "functions"
    rules_key = "rules"

    variables_allowed_tags = (Include,)
    functions_allowed_tags = (Include, Ref, IRef, Keys, Values)
    rules_allowed_tags = (Include, Ref, IRef, Keys, Values, IncludeRules)

    def __init__(self, data):
        self.id = data[self.id_key]
        self.variables = Section(
            data=data.get(self.variables_key, {}),
            name=self.variables_key,
            allowed_tags=self.variables_allowed_tags,
        )

        self.functions = Section(
            data=data.get(self.functions_key, {}),
            name=self.functions_key,
            allowed_tags=self.functions_allowed_tags,
        )

        self.rules = Section(
            data=data.get(self.rules_key, {}),
            name=self.rules_key,
            allowed_tags=self.rules_allowed_tags
        )

    def resolve(self, resolver):
        self.variables = resolver.resolve_section(
            section=self.variables, scope=self)
        self.functions = resolver.resolve_section(
            section=self.variables, scope=self)
        self.rules = resolver.resolve_section(section=self.rules, scope=self)
        return self

    def lookup_variable(self, ref):
        return nested_get(self.variables.data, ref.split("."))


class Resolver(object):
    def __init__(self, loader, irefs=None):
        self.loader = loader
        self.irefs = irefs or {}

    def lookup_iref(self, ref):
        return nested_get(self.irefs, ref.split("."))

    def resolve(self, data):
        scope = Scope(data)
        res = self.resolve_scope(scope)
        if not res:
            raise Exception("failed to resolve scope, id:{}".format(scope.id))
        return res

    def resolve_scope(self, scope):
        return scope.resolve(self)

    def resolve_dict(self, data, scope=None, allowed_tags=None, section_name=None):
        def _recur(node, func, delegate=True):
            if isinstance(node, dict):
                return {k: _recur(v, func, delegate) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func, delegate) for v in node]
            elif isinstance(node, Delegate) and delegate:
                return node.delegate(func, scope)
            return func(node, scope)

        data = _recur(data, self._filter_nodes(
            Include, allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            (Ref, IRef), allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            (Keys, Values), allowed_tags, section_name), delegate=False)
        data = _recur(data, self._filter_nodes(
            IncludeRules, allowed_tags, section_name))
        return data

    def resolve_section(self, section, scope=None):
        return section.resolve(self, scope)

    def _filter_nodes(self, node_clss, allowed_tags=None, section_name=None):
        forbidden = cls_diff(SCULPT_TAGS, allowed_tags)

        def _filter(node, scope):
            if isinstance(node, forbidden):
                raise Exception("tag {} not allowed in '{}' section".format(
                    node.yaml_tag, section_name))
            if isinstance(node, node_clss):
                return node.resolve(self, scope)
            return node

        return _filter


def cls_diff(right, left):
    if right is None or left is None:
        return ()

    out = []
    for c in right:
        if c not in left:
            out.append(c)
    return tuple(out)


class Loader(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def load(self, data):
        _loader = get_loader(data)
        return _loader.get_single_data()

    def load_file(self, filename):
        path = os.path.join(self.root_dir, filename)
        with open(path) as source:
            return self.load(source)
