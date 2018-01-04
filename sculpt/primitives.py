from sculpt.operations import Each, Copy, Delete
from sculpt.fields import VirtualList
from sculpt.core import execute_operations


class FieldSelect(object):
    def __init__(self, left, field_label, right):
        self.left = left
        self.right = right
        self.field_label = field_label

    def run(self, context):
        left_cls = self.left.__class__
        right_cls = self.right.__class__

        execute_operations(context, [
            Each(left_cls(self.left.label), right_cls(self.right.label), [
                Copy(left_cls(self.field_label), VirtualList("_").append()),
            ]),
            Copy(VirtualList("_"), right_cls(self.right.label)),
            Delete(VirtualList("_"))
        ])
