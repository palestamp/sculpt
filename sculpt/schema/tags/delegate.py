
class Delegate(object):
    def delegate(self, func, scope):
        self.obj = func(self.obj, scope)
        return self
    
