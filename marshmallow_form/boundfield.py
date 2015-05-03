# -*- coding:utf-8 -*-
import copy
from collections import ChainMap
from marshmallow.compat import text_type
from .lazylist import LazyList
from .langhelpers import reify, Counter


def field(fieldclass, *args, **kwargs):
    return Field(fieldclass(*args, **kwargs))


C = Counter(0)
MARKER = object()  # adhoc


class Field(object):
    def __init__(self, field, name=None):
        self.field = field
        self.name = name
        self._c = C()

    def expose(self):
        return self.field

    def __get__(self, ob, type_):
        if ob is None:
            return self
        name = self.name
        field = ob.schema.fields[name]
        bf = bound_field(name, field, ob, overrides=ob.metadata.get(name))
        ob.__dict__[name] = bf
        return bf


def bound_field(name, field, ob, key=None, overrides=None, parent_errors=None):
    parent_errors = parent_errors or set()
    if hasattr(field, "nested"):
        if field.many:
            return NestedListBoundField(name, field, ob, overrides=overrides, parent_errors=parent_errors)
        else:
            return NestedBoundField(name, field, ob, key=key, overrides=overrides, parent_errors=parent_errors)
    else:
        return BoundField(name, field, ob, key=key, overrides=overrides, parent_errors=parent_errors)


class BoundField(object):
    def __init__(self, name, field, form, key=None, overrides=None, parent_errors=None):
        self.name = name
        self.key = key or name
        self.field = field
        self.form = form
        self.overrides = overrides
        self.parent_errors = parent_errors

    def __iter__(self):
        yield self

    @reify
    def metadata(self):
        if self.overrides:
            return ChainMap(self.overrides, self.field.metadata)
        else:
            return self.field.metadata

    @property
    def errors(self):
        return (self.form.errors.get(self.key) or [])

    @property
    def fullerrors(self):
        return self.errors + list(self.parent_errors or [])

    def __call__(self, *args, **kwargs):
        if "__call__" in self.metadata:
            return self.metadata["__call__"](self, *args, **kwargs)
        return self.value

    def __getitem__(self, k):
        return self.form.itemgetter(self.metadata, k)

    def __getattr__(self, k):
        return getattr(self.field, k, None) or []

    def disabled(self):
        self.metadata["disabled"] = True

    @reify
    def choices(self):
        if "pairs" in self.metadata:
            return self.metadata["pairs"]
        elif hasattr(self.field, "labels"):
            labelgetter = self.metadata.get("labelgetter") or text_type
            return LazyList(self.field.labels(labelgetter))
        else:
            return []

    @reify
    def value(self):
        return (self.form.data.get(self.key)
                or self.form.initial.get(self.key)
                or self.form.rawdata.get(self.key)
                or self.field.default)


class SubForm(object):
    def __init__(self, data, rawdata, errors, initial, itemgetter):
        self.data = data
        self.rawdata = rawdata
        self.errors = errors
        self.initial = initial
        self.itemgetter = itemgetter

    @classmethod
    def from_form(cls, name, form, used_parent_errors=None):
        if hasattr(form.data, "get"):
            data = (form.data.get(name) if form.data else None) or {}
            rawdata = (form.rawdata.get(name) if form.rawdata else None) or {}
        else:
            data = form.data[name]
            rawdata = form.rawdata[name]

        # errors are occured in parent form, errors dict is already flatten. so.
        errors = (form.errors.get(name) if hasattr(form.errors, "get") else None) or {}

        initial = (form.initial.get(name) if form.initial else None) or {}
        return cls(data, rawdata, errors, initial, itemgetter=form.itemgetter)


class NestedBoundField(BoundField):
    allkey = "_schema"

    def __init__(self, name, field, form, overrides=None, key=None, parent_errors=None):
        self._name = name
        self.key = key if key is not None else name
        self.field = field
        self.form = form
        self.overrides = overrides
        self.parent_errors = parent_errors

    @reify
    def children(self):
        return copy.deepcopy(self.field.nested._declared_fields)

    @property
    def errors(self):
        return (self.form.errors.get(self.key) or {}).get(self.allkey) or []

    def __iter__(self):
        for k in self.children.keys():
            for f in getattr(self, k):
                yield f

    def __getattr__(self, k):
        if k not in self.children:
            raise AttributeError(k)
        subform = SubForm.from_form(self.key, self.form)
        name = "{}.{}".format(self._name, k)

        # propagating parent form's errors. using via self.fullerrors
        parent_errors = self.parent_errors
        if self.form.errors is not None:
            if self.key in self.form.errors:
                current_errors = self.form.errors[self.key]
                if not hasattr(current_errors, "get"):
                    parent_errors.update(current_errors)

            # errors are occured in parent form, errors dict is already flatten. so.
            if not hasattr(self.form.errors, "get"):
                parent_errors.update(self.form.errors)

        bf = bound_field(name, self.children[k], subform, key=k,
                         overrides=self.metadata.get(k), parent_errors=parent_errors)
        setattr(self, k, bf)
        return bf


class NestedListBoundField(BoundField):
    def __init__(self, name, field, form, overrides=None, parent_errors=None):
        self._name = name
        self.field = field
        self.form = form
        self.overrides = overrides
        self.parent_errors = parent_errors

    @reify
    def children(self):
        initial = (self.form.initial.get(self._name) if self.form.initial else None) or {}
        rawdata = (self.form.rawdata.get(self._name) if self.form.rawdata else None) or {}
        errors = (self.form.errors.get(self._name) if self.form.errors else None) or {}
        overrides = (self.overrides.get(self._name) if self.overrides else None) or {}
        itemgetter = self.form.itemgetter
        field = self.field
        data = self.form.data[self._name]
        return LazyList(NestedBoundField("{}.{}".format(self._name, i), field, SubForm(data, rawdata, errors, initial, itemgetter=itemgetter), key=i, overrides=overrides)
                        for i in range(len(data)))

    def __iter__(self):
        for c in self.children:
            yield c

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.children[i]
        else:
            return self.form.itemgetter(self.metadata, i)

    def __getattr__(self, k):
        raise AttributeError(k)
