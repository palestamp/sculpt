from .yml import register_tag
from .resolver import Loader, Resolver

from .tags import Include, Ref, IRef, Keys, Values, IncludeRules
from .tags import SCULPT_TAGS


for tag in SCULPT_TAGS:
    register_tag(tag)
