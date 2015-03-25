from .exceptions import (
    LayoutTooFew,
    LayoutTooMany
)


class Layout(object):
    def __init__(self, shape):
        self.shape = shape

    def set_from_shape(self, shape, s):
        if isinstance(shape, (tuple, list, LColumn)):
            for row in shape:
                self.set_from_shape(row, s)
        else:
            s.add(shape)

    def check_shape(self, form):
        actual_set = set()
        self.set_from_shape(self.shape, actual_set)
        expected_set = set(bf.name for bf in form)
        diff = expected_set.difference(actual_set)
        if diff:
            raise LayoutTooFew(diff)
        diff = actual_set.difference(expected_set)
        if diff:
            raise LayoutTooMany(diff)

    def build_iterator(self, form, shape):
        if isinstance(shape, (list, tuple)):
            return [self.build_iterator(form, row) for row in shape]
        elif isinstance(shape, LColumn):
            fields = [self.build_iterator(form, row) for row in shape]
            return (shape, fields)
        else:
            target = form
            for k in shape.split("."):
                target = getattr(target, k)
            return target

    def __call__(self, form):
        return iter(self.build_iterator(form, self.shape))


class LColumn(object):
    def __init__(self, *fields, **metadata):
        self.fields = fields
        self.metadata = metadata

    def __getitem__(self, k):
        return self.metadata[k]

    def __iter__(self):
        return iter(self.fields)


class FlattenLayout(object):
    def __call__(self, form):
        for name in form.ordered_names:
            for bfield in getattr(form, name):
                yield bfield
