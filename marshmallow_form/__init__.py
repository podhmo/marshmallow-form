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
        bf = self.bound_field(name, ob)
        ob.__dict__[name] = bf
        return bf

    def bound_field(self, name, ob):
        return BoundField(name, ob.schema.fields[name], ob)


class BoundField(object):
    def __init__(self, name, field, form):
        self.name = name
        self.field = field
        self.form = form

    @property
    def metadata(self):
        return self.field.metadata

    def __getitem__(self, k):
        return self.field.metadata[k]

    def __getattr__(self, k):
        return getattr(self.field, k)

    def disabled(self):
        self.metadata["disabled"] = True

    @reify
    def choices(self):
        labelgetter = self.metadata.get("labelgetter") or text_type
        return LazyList(self.field.labels(labelgetter))

    @reify
    def value(self):
        return (self.form.data.get(self.name)
                or self.form.initial.get(self.name))


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


class FormBase(object):
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
            yield getattr(self, name)

    def cleansing(self, data=None):
        data = data or self.data
        d = {}
        for k, f in self.schema.fields.items():
            v = data.get(self.prefix + k, "")
            if v == "" and not isinstance(f, fields.String):
                continue
            d[k] = v
        return d

    def has_errors(self):
        return bool(self.errors)

    def deserialize(self, data=None):
        data = data or self.data
        data = self.cleansing(data)
        result = self.schema.load(data)
        self.errors = result.errors
        return result.data

    def serialize(self, data=None):
        data = data or self.data
        return self.schema.dump(data)


Form = FormMeta("Form", (FormBase, ), {})


# TODO:
class ModelForm(Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        super(ModelForm, self).__init__(*args, **kwargs)


NestedField = partial(field, fields.Nested)

PriceField = partial(field, fields.Price, required=True)
ArbitraryField = partial(field, fields.Arbitrary, required=True)
DecimalField = partial(field, fields.Decimal, required=True)
DateTimeField = partial(field, fields.DateTime, required=True)
URLField = partial(field, fields.URL, required=True)
TimeField = partial(field, fields.Time, required=True)
StrField = partial(field, fields.Str, required=True)
BoolField = partial(field, fields.Bool, required=True)
StringField = partial(field, fields.String, required=True)
UrlField = partial(field, fields.Url, required=True)
LocalDateTimeField = partial(field, fields.LocalDateTime, required=True)
FloatField = partial(field, fields.Float, required=True)
EmailField = partial(field, fields.Email, required=True)
DateField = partial(field, fields.Date, required=True)
FieldField = partial(field, fields.Field, required=True)
IntField = partial(field, fields.Int, required=True)
EnumField = partial(field, fields.Enum, required=True)
TimeDeltaField = partial(field, fields.TimeDelta, required=True)
UUIDField = partial(field, fields.UUID, required=True)
FunctionField = partial(field, fields.Function, required=True)
FormattedStringField = partial(field, fields.FormattedString, required=True)
NumberField = partial(field, fields.Number, required=True)
MethodField = partial(field, fields.Method, required=True)
RawField = partial(field, fields.Raw, required=True)
SelectField = partial(field, fields.Select, required=True)
FixedField = partial(field, fields.Fixed, required=True)
QuerySelectField = partial(field, fields.QuerySelect, required=True)
ValidatedFieldField = partial(field, fields.ValidatedField, required=True)
IntegerField = partial(field, fields.Integer, required=True)
QuerySelectListField = partial(field, fields.QuerySelectList, required=True)
BooleanField = partial(field, fields.Boolean, required=True)
ListField = partial(field, fields.List, required=True)

# from prestring.python import PythonModule
# m = PythonModule()
# for k, v in fields.__dict__.items():
#     if isinstance(v, type) and issubclass(v, fields.Field):
#         m.stmt("{}Field = partial(field, fields.{})".format(k, k))
# print(m)
