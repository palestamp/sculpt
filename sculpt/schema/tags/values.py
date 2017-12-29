from .keys import KVViewTag
from .exceptions import TagError


class BadValues(TagError):
    def __str__(self):
        return 'Bad values, {}: !values {}, at line:{}'.format(
            self.args[0], self.args[1], self.lineno)


class Values(KVViewTag):
    yaml_tag = u'!values'
    exc_type = BadValues

    def __init__(self, obj, lineno=None):
        self.obj = obj
        self.__lineno__ = lineno

    def __repr__(self):
        return 'Values({})'.format(self.obj)
