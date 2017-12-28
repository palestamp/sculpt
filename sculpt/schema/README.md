# Schema-specific tags

## !include

> Accepts string in URL format, fragment specifies nested path.
> Supported schemes: file

Include tag replace its position with content that is placed under URL address.

For example `!include 'file://child.yml#variables.region'` will be replaced with
content of `child.yml` (found relatively to Loader root_dir) from nested key `variables.region`

## !ref

> Accepts string which specifies path to target variable in `variable` section.

Reference tag *renders* variable from `variables` section of current scope using nested path, 
for example `regions.names`.

## !iref

> Accepts string which specifies path to target variable in `Resolver.irefs`.

Reference tag *renders* variable with value provided in `Resolver` initialization.

## !include-rules

> Accepts string in URL format, fragment part is forbidden.
> Supported schemes: file

This tags gives a possibilty to extend parent rules with child rules. Child source structure
is ordinary structure of rules file. Child source creates its own scope, it does not see parent scope, and has no way to access it. Also this means that child scope is self-contained and can not be polluted with
parent variables. The same applies to `functions`.

This tag returns child `rules` section which is fully rendered.
Usage of URL fragment in `!include-rules` will raise exception.

## !keys and !values

> Accepts object, in format `{map: $value}`, 'map' key required.
> `$value` can be `!ref` or `!iref` which should be rendered to dictionary, also
> value can be dict literal. 

These tags acts as python `.keys()` and `.values()` dict methods.

# Schema resolution order:

Schema is loaded in next steps:

1. YAML parsing
2. Static tag resolution
3. Function compilation
4. Rules compilation 

These to steps are separate.

## First - 'variables'
This section is resolved first, only `!include` tag is supported for 
use in this section, the result of usage of other tags is undefined.
Usage of unsopported tags will not raise an error, though this can 
change in future.

## Second - 'functions'
Supports `!include`, `!ref`, `!iref`, `!keys` and `!values` tags.

## Third - 'rules'
This section supports all tags


# Tags resolution order

Each sections contents  resolved in next order:

1. All `!include` tags resolved first.
2. `!ref` and `!iref` tags.
3. `!keys` and `!values` tags.
4. `!include-rules` tag resolved last.

