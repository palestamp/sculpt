



try:
    basestring  # pylint:disable=undefined-variable
    def isstr(s):
        return isinstance(s, basestring) # pylint:disable=undefined-variable
except NameError:
    def isstr(s):
        return isinstance(s, str)
