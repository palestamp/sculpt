
try:
    basestring  # pylint:disable=undefined-variable,pointless-statement
    def isstr(obj):
        return isinstance(obj, basestring) # pylint:disable=undefined-variable
except NameError:
    def isstr(obj):
        return isinstance(obj, str)
