class TagError(Exception):
    def __init__(self, *args, **kwargs):
        super(TagError, self).__init__(self, *args)
        self.lineno = kwargs.get('lineno', 'unknown')
        self.args = args
