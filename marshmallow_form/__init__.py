# -*- coding:utf-8 -*-
import logging
from functools import partial
from marshmallow import fields
from marshmallow.compat import text_type
from .lazylist import LazyList
logger = logging.getLogger(__name__)


class reify(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Counter(object):
    def __init__(self, i):
        self.i = i

    def __call__(self):
        v = self.i
        self.i += 1
        return v

C = Counter(0)


class Field(object):
    def __init__(self, field):
        self.field = field
        self.name = None
        self._c = C()

    def expose(self):
        return self.field

    def __get__(self, ob, type_):
        if ob is None:
            return self
        name = self.name
        field = ob.schema.fields[name]
        bf = bound_field(name, field, ob)
        ob.__dict__[name] = bf
        return bf


def bound_field(name, field, ob, key=None):
    if hasattr(field, "nested"):
        return NestedBoundField(name, field, ob)
    else:
        return BoundField(name, field, ob, key=key)


class BoundField(object):
    def __init__(self, name, field, form, key=None):
        self.name = name
        self.key = key or name
        self.field = field
        self.form = form

    def __iter__(self):
        yield self

    @property
    def metadata(self):
        return self.field.metadata

    def __getitem__(self, k):
        return self.form.itemgetter(self.metadata, k)

    def __getattr__(self, k):
        return getattr(self.field, k)

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
                or self.field.default)


class SubForm(object):
    def __init__(self, data, initial, itemgetter):
        self.data = data
        self.initial = initial
        self.itemgetter = itemgetter

    @classmethod
    def from_form(cls, name, form):
        data = (form.data.get(name) if form.data else None) or {}
        initial = (form.initial.get(name) if form.initial else None) or {}
        return cls(data, initial, itemgetter=form.itemgetter)


class NestedBoundField(BoundField):
    def __init__(self, name, field, form):
        self._name = name
        self.field = field
        self.children = field.nested._declared_fields
        self.form = form

    def __iter__(self):
        for k in self.children.keys():
            yield getattr(self, k)

    @property
    def metadata(self):
        return self.field.metadata

    def __getitem__(self, k):
        return self.form.itemgetter(self.metadata, k)

    def __getattr__(self, k):
        if k not in self.children:
            raise AttributeError(k)
        subform = SubForm.from_form(self._name, self.form)
        bf = bound_field("{}.{}".format(self._name, k), self.children[k], subform, key=k)
        setattr(self, k, bf)
        return bf


def field(fieldclass, *args, **kwargs):
    return Field(fieldclass(*args, **kwargs))


class FormMeta(type):
    from marshmallow import Schema
    SchemaBase = Schema

    def __new__(self, name, bases, attrs):
        schema_attrs = {}
        fields = []
        for k, v in attrs.items():
            if hasattr(v, "expose"):
                v.name = k
                schema_attrs[k] = v.expose()
                fields.append(v)
        attrs["ordered_names"] = [f.name for f in sorted(fields, key=lambda f: f._c)]
        schema_class = self.SchemaBase.__class__(name.replace("Form", "Schema"), (self.SchemaBase, ), schema_attrs)
        attrs["schema_factory"] = schema_class
        return super().__new__(self, name, bases, attrs)


class FlattenFormBase(object):
    itemgetter = staticmethod(lambda d, k: d.get(k, ""))

    def __init__(self, data=None, initial=None, prefix="", options={"strict": False}):
        self.options = options
        self.rawdata = data or {}
        self.data = self.rawdata.copy()
        self.initial = initial or {}
        self.errors = None
        self.prefix = prefix

    @reify
    def schema(self):
        return self.schema_factory(**self.options)

    def add_field(self, name, field):
        if hasattr(field, "expose"):
            field = field.expose()
        self.schema.fields[name] = field
        setattr(self, name, BoundField(name, field, self))

    def remove_field(self, name):
        if hasattr(self, name):
            delattr(self, name)
            del self.schema.fields[name]
        if "ordered_names" not in self.__dict__:
            self.ordered_names = self.ordered_names[:]
        self.ordered_names.remove(name)

    def __iter__(self):
        for name in self.ordered_names:
            for bfield in getattr(self, name):
                yield bfield

    def _parsing_iterator(self, name, field):
        if hasattr(field, "nested"):
            for subname, f in field.nested._declared_fields.items():
                for subname, subf in self._parsing_iterator(subname, f):
                    yield "{}.{}".format(name, subname), subf
        else:
            yield name, field

    def cleansing(self, data=None):
        data = data or self.data
        result = d = {}
        for name, f in self.schema.fields.items():
            for k, f in self._parsing_iterator(name, f):
                d = result
                v = data.get(self.prefix + k, "")
                if v == "" and not isinstance(f, fields.String):
                    continue
                ts = k.split(".")
                for t in ts[:-1]:
                    if t not in d:
                        d[t] = {}
                    d = d[t]
                d[ts[-1]] = v
        return result

    def has_errors(self):
        return bool(self.errors)

    def deserialize(self, data=None, cleansing=True):
        data = data or self.data
        if cleansing:
            data = self.cleansing(data)
        result = self.schema.load(data)
        self.errors = result.errors
        return result.data

    def serialize(self, data=None):
        data = data or self.data
        return self.schema.dump(data)


Form = FlattenForm = FormMeta("FlattenForm", (FlattenFormBase, ), {})


# TODO:
class ModelForm(Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        super(ModelForm, self).__init__(*args, **kwargs)


def select_wrap(pairs, *args, **kwargs):
    choices = [p[0] for p in pairs]
    kwargs["pairs"] = pairs
    return fields.Select(choices, *args, **kwargs)


def nested_wrap(formclass, *args, **kwargs):
    schema = formclass.schema_factory
    return fields.Nested(schema, *args, **kwargs)


if __name__ != "__main__":
    Nested = partial(field, nested_wrap, required=True)

    Price = partial(field, fields.Price, required=True)
    Arbitrary = partial(field, fields.Arbitrary, required=True)
    Decimal = partial(field, fields.Decimal, required=True)
    DateTime = partial(field, fields.DateTime, required=True)
    URL = partial(field, fields.URL, required=True)
    Time = partial(field, fields.Time, required=True)
    Str = partial(field, fields.Str, required=True)
    Bool = partial(field, fields.Bool, required=True)
    String = partial(field, fields.String, required=True)
    Url = partial(field, fields.Url, required=True)
    LocalDateTime = partial(field, fields.LocalDateTime, required=True)
    Float = partial(field, fields.Float, required=True)
    Email = partial(field, fields.Email, required=True)
    Date = partial(field, fields.Date, required=True)
    Int = partial(field, fields.Int, required=True)
    TimeDelta = partial(field, fields.TimeDelta, required=True)
    UUID = partial(field, fields.UUID, required=True)
    Function = partial(field, fields.Function, required=True)
    FormattedString = partial(field, fields.FormattedString, required=True)
    Number = partial(field, fields.Number, required=True)
    Method = partial(field, fields.Method, required=True)
    Raw = partial(field, fields.Raw, required=True)
    Select = partial(field, select_wrap, required=True)
    Fixed = partial(field, fields.Fixed, required=True)
    QuerySelect = partial(field, fields.QuerySelect, required=True)
    ValidatedField = partial(field, fields.ValidatedField, required=True)
    Integer = partial(field, fields.Integer, required=True)
    QuerySelectList = partial(field, fields.QuerySelectList, required=True)
    Boolean = partial(field, fields.Boolean, required=True)
    List = partial(field, fields.List, required=True)

# from prestring.python import PythonModule
# m = PythonModule()
# for k, v in fields.__dict__.items():
#     if isinstance(v, type) and issubclass(v, fields.):
#         m.stmt("{} = partial(field, fields.{})".format(k, k))
# print(m)
