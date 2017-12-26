
DEFINES_KEY = 'define'


class FunctionCompiler(object):
    @classmethod
    def from_dict(cls, data):
        defines = data.get(DEFINES_KEY, [])
