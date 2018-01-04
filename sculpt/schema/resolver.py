import os
from operator import methodcaller


from .tags import (NestedTag, Include, Ref, IRef,
                   Keys, Values, IncludeRules, Fn)
from .tags import SCULPT_TAGS
from .resolvers import (FnResolver, IncludeResolver, IncludeRulesResolver,
                        KeysResolver, ValuesResolver, RefResolver, IRefResolver)
from .yml import get_loader
from .util import nested_access


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
            section_name=self.name
        )

        return Section(
            data=res,
            allowed_tags=self.allowed_tags,
            name=self.name
        )

    @classmethod
    def factory(cls, data, **kwargs):
        allow_ordered_definition = kwargs.pop("allow_ordered_definition", False)
        if allow_ordered_definition and isinstance(data, list):
            return NamespaceSection(data, **kwargs)

        return Section(data, **kwargs)


class NamespaceSection(Section):
    def resolve(self, resolver, scope=None):
        res = resolver.resolve_namespace_list(
            data=self.data,
            scope=scope,
            allowed_tags=self.allowed_tags,
            section_name=self.name
        )

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
    functions_allowed_tags = (Include, Ref, IRef, Keys, Values, Fn)
    rules_allowed_tags = (Include, Ref, IRef, Keys, Values, IncludeRules, Fn)

    def __init__(self, data):
        self.ident = data[self.id_key]
        self.variables = Section.factory(
            data=data.get(self.variables_key, {}),
            name=self.variables_key,
            allowed_tags=self.variables_allowed_tags,
        )

        self.functions = Section.factory(
            data=data.get(self.functions_key, {}),
            name=self.functions_key,
            allowed_tags=self.functions_allowed_tags,
            allow_ordered_definition=True,
        )

        self.rules = Section.factory(
            data=data.get(self.rules_key, {}),
            name=self.rules_key,
            allowed_tags=self.rules_allowed_tags
        )

    def resolve(self, resolver):
        self.variables = resolver.resolve_section(
            section=self.variables, scope=self)
        self.functions = resolver.resolve_section(
            section=self.functions, scope=self)
        self.rules = resolver.resolve_section(section=self.rules, scope=self)
        return self

    def lookup_variable(self, ref):
        return nested_access(self.variables.data, ref.split("."))

    def lookup_function(self, ref):
        return nested_access(self.functions.data, ref.split("."))


class ScopeProxy(Scope):
    def __init__(self, scope=None):
        super(ScopeProxy, self).__init__({self.id_key: "__fake__"})
        self._scopes = []
        self.push(scope)

    def push(self, scope):
        if scope:
            self._scopes.append(scope)

    def _chain_lookup(self, method_call):
        for scope in reversed(self._scopes):
            found, value = method_call(scope)
            if found:
                return found, value
        return False, None

    def lookup_variable(self, ref):
        return self._chain_lookup(methodcaller('lookup_variable', ref))

    def lookup_function(self, ref):
        return self._chain_lookup(methodcaller('lookup_function', ref))


class Resolver(object):
    def __init__(self, loader, irefs=None, tag_resolvers=None):
        self.loader = loader

        self.irefs = irefs or {}

        tag_resolvers = tag_resolvers or {}
        self._tag_registry = self._register_tags(tag_resolvers)

    def _register_tags(self, tag_resolvers):
        default_registry = {
            Fn.yaml_tag: FnResolver(),
            Include.yaml_tag: IncludeResolver(),
            IncludeRules.yaml_tag: IncludeRulesResolver(),
            Keys.yaml_tag: KeysResolver(),
            Values.yaml_tag: ValuesResolver(),
            Ref.yaml_tag: RefResolver(),
            IRef.yaml_tag: IRefResolver(),
        }

        default_registry.update(tag_resolvers)
        return default_registry

    def lookup_iref(self, ref):
        return nested_access(self.irefs, ref.split("."))

    def resolve(self, data):
        scope = Scope(data)
        res = self.resolve_scope(scope)
        if not res:
            raise Exception("failed to resolve scope, id:{}".format(scope.ident))
        return res

    def resolve_scope(self, scope):
        return scope.resolve(self)

    def resolve_section(self, section, scope=None):
        return section.resolve(self, scope)

    def resolve_tag(self, scope, tag):
        resolver = self._tag_registry[tag.yaml_tag]
        return resolver.resolve(self, scope, tag)

    def resolve_dict(self, data, scope=None, allowed_tags=None, section_name=None):
        def _recur(node, func):
            if isinstance(node, dict):
                return {k: _recur(v, func) for k, v in node.items()}
            elif isinstance(node, list):
                return [_recur(v, func) for v in node]
            elif isinstance(node, NestedTag):
                node = node.delegate(func, scope)
            return func(node, scope)

        data = _recur(data, self._filter_nodes(
            Include, allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            (Ref, IRef), allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            (Keys, Values), allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            IncludeRules, allowed_tags, section_name))
        data = _recur(data, self._filter_nodes(
            Fn, allowed_tags, section_name))
        return data

    def resolve_namespace_list(self, data, scope=None, allowed_tags=None, section_name=None):
        lookup_proxy = ScopeProxy(scope)

        out = {}
        for namespace_dict in data:
            name = namespace_dict["namespace"]
            content = namespace_dict["items"]
            data = self.resolve_dict(content, lookup_proxy, allowed_tags, section_name)
            scoped_data = {name: data}

            tmp_scope = Scope({
                Scope.id_key: "__fake__",
                section_name: scoped_data
            })
            lookup_proxy.push(tmp_scope)

            out.update(scoped_data)

        return out

    def _filter_nodes(self, node_clss, allowed_tags=None, section_name=None):
        forbidden = cls_diff(SCULPT_TAGS, allowed_tags)

        def _filter(node, scope):
            if isinstance(node, forbidden):
                raise Exception("tag {} not allowed in '{}' section".format(
                    node.yaml_tag, section_name))
            if isinstance(node, node_clss):
                return self.resolve_tag(scope, node)
            return node

        return _filter


def cls_diff(right, left):
    if right is None or left is None:
        return ()

    out = []
    for cls in right:
        if cls not in left:
            out.append(cls)
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
