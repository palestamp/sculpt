
class Element(object):
    __eq_attrs__ = []

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            self_vals = [getattr(self, name) for name in self.__eq_attrs__]
            other_vals = [getattr(other, name) for name in self.__eq_attrs__]
            if not self_vals or not other_vals:
                return NotImplemented
            return self_vals == other_vals
        return NotImplemented

    def __ne__(self, other):
        equals = self.__eq__(other)
        if equals is not NotImplemented:
            return not equals
        return NotImplemented
