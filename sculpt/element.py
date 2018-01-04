
class Element(object):
    __el_name__ = "base"

    def accept(self, visitor):
        method_name = 'visit_{}'.format(self.__el_name__)
        visit = getattr(visitor, method_name, None)
        if not visit:
            visit = getattr(visitor, "visit_default")
        return visit(self)
