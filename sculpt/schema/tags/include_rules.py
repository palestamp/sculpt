from .include import Include


class IncludeRules(Include):
    yaml_tag = u'!include-rules'

    def __repr__(self):
        return 'IncludeRules({})'.format(self.url)
