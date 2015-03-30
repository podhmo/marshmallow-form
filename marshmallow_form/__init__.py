# -*- coding:utf-8 -*-
import logging
import copy
from functools import partial
from marshmallow import fields
from marshmallow.exceptions import MarshallingError
from .langhelpers import reify
from .layout import FlattenLayout
from .boundfield import (
    field,
    Field,
    BoundField
)
logger = logging.getLogger(__name__)


class RegisterAction(object):
    def __init__(self, action, method):
        self.action = action
        self.method = method

    def register(self, schema):
        self.action(schema, self.method)


class FormMeta(type):
    from marshmallow import Schema
    SchemaBase = Schema

    @staticmethod
    def access(self, k, ob):
        return getattr(ob, k)

    @classmethod
    def from_schema(self, name, schema, bases, attrs, meta=object()):
        attrs["Schema"] = schema
        metadata = attrs["metadata"] = {}

        layout = None
        layout = getattr(meta, "layout", None)
        metadata.update(getattr(meta, "metadata", {}))
        metadata.update(getattr(meta, "overrides", {}))
        if hasattr(meta, "itemgetter"):
            if isinstance(meta.itemgetter, staticmethod):
                attrs["itemgetter"] = meta.itemgetter
            else:
                attrs["itemgetter"] = staticmethod(meta.itemgetter)

        boundary_container = []
        for k, f in schema._declared_fields.items():
            attrs[k] = Field(f, name=k)
            boundary_container.append(attrs[k])
        for field_name in getattr(meta, "fields", []):
            if field_name not in attrs:
                attrs[field_name] = Field(None, name=field_name)
                boundary_container.append(attrs[field_name])

        attrs["ordered_names"] = [f.name for f in sorted(boundary_container, key=lambda f: f._c)]

        cls = super(FormMeta, self).__new__(self, name, bases, attrs)

        if layout is not None:
            layout.check_shape(cls())
        cls.layout = layout or FlattenLayout()

        cls.metadata = metadata
        return cls

    def __new__(self, name, bases, attrs):
        # todo: rewrite
        # - collecting schema
        # - make_object
        # - layout

        schema_attrs = {}
        boundary_container = {}
        register_actions = []
        schema_bases = []
        metadata = {}

        for b in bases:
            if hasattr(b, "ordered_names"):
                for k in b.ordered_names:
                    v = getattr(b, k)
                    schema_attrs[k] = v.expose()
                    boundary_container[k] = v
            if hasattr(b, "metadata"):
                metadata.update(b.metadata)
            if hasattr(b, "Schema") and issubclass(b.Schema, self.Schema):
                if b.Schema not in schema_bases:
                    schema_bases.append(b.Schema)
        if len(schema_bases) <= 0:
            schema_bases.append(self.SchemaBase)

        for k, v in attrs.items():
            if hasattr(v, "expose"):
                v.name = k
                schema_attrs[k] = v.expose()
                boundary_container[k] = v
            if hasattr(v, "register") and callable(v.register):
                register_actions.append(v)

        # this is meta of marshmallow Schema
        class Meta:
            ordered = True
        schema_attrs["Meta"] = Meta

        layout = None
        if "Meta" in attrs:
            meta = attrs["Meta"]
            layout = getattr(meta, "layout", None)
            metadata.update(getattr(meta, "metadata", {}))
            metadata.update(getattr(meta, "overrides", {}))
            if hasattr(meta, "itemgetter"):
                if isinstance(meta.itemgetter, staticmethod):
                    attrs["itemgetter"] = meta.itemgetter
                else:
                    attrs["itemgetter"] = staticmethod(meta.itemgetter)
            if hasattr(meta, "fields"):
                for field_name in meta.fields:
                    if field_name not in attrs:
                        v = Field(None, name=field_name)
                        attrs[field_name] = v
                        boundary_container[field_name] = v
                Meta.fields = attrs["Meta"].fields

        if "make_object" in attrs:
            schema_attrs["make_object"] = attrs.pop("make_object")

        attrs["ordered_names"] = [f.name for f in sorted(boundary_container.values(), key=lambda f: f._c)]
        attrs["register_actions"] = register_actions
        schema_class = self.SchemaBase.__class__(
            name.replace("Form", "Schema"),
            tuple(schema_bases),
            schema_attrs)
        # schema_class.accessor(self.access)
        attrs["Schema"] = schema_class

        cls = super(FormMeta, self).__new__(self, name, bases, attrs)

        if layout is not None:
            layout.check_shape(cls())
        cls.layout = layout or FlattenLayout()

        cls.metadata = metadata

        for ac in register_actions:
            ac.register(cls.Schema)
        return cls


class FormBase(object):
    itemgetter = staticmethod(lambda d, k: d.get(k, ""))
    error_handler = partial(RegisterAction, (lambda schema, method: schema.error_handler(method)))
    data_handler = partial(RegisterAction, (lambda schema, method: schema.data_handler(method)))
    validator = partial(RegisterAction, (lambda schema, method: schema.validator(method)))
    preprocessor = partial(RegisterAction, (lambda schema, method: schema.preprocessor(method)))
    accessor = partial(RegisterAction, (lambda schema, method: schema.accessor(method)))

    def __init__(self, data=None, initial=None, prefix="", options={"strict": False}, metadata=None):
        self.options = options
        self.rawdata = data or {}
        self.data = self.rawdata.copy()
        self.initial = initial or {}
        self.errors = None
        self.prefix = prefix
        self.metadata = copy.deepcopy(self.metadata)
        if metadata:
            self.metadata.update(metadata)

    @reify
    def _update_fields_option(self):
        return len(self.schema.fields) != len(self.schema.declared_fields)

    @reify
    def schema(self):
        return self.Schema(**self.options)

    @classmethod
    def from_object(cls, ob, *args, **kwargs):
        form = cls(*args, **kwargs)
        data = form.serialize(ob)
        form.rawdata = data
        form.data = data.copy()
        return form

    def add_field(self, name, field):
        if hasattr(field, "expose"):
            field = field.expose()
        self.schema.fields[name] = field
        if "ordered_names" not in self.__dict__:
            self.ordered_names = self.ordered_names[:]
        self.ordered_names.append(name)
        setattr(self, name, BoundField(name, field, self))

    def remove_field(self, name):
        if hasattr(self, name):
            delattr(self, name)
            del self.schema.fields[name]
        if "ordered_names" not in self.__dict__:
            self.ordered_names = self.ordered_names[:]
        self.ordered_names.remove(name)

    def __iter__(self):
        return iter(self.layout(self))

    def _parsing_iterator(self, name, field):
        if hasattr(field, "nested"):
            for subname, f in field.schema.fields.items():
                for subname, subf in self._parsing_iterator(subname, f):
                    yield "{}.{}".format(name, subname), subf
        else:
            yield name, field

    def cleansing(self, data=None):
        data = data or self.rawdata
        result = d = {}
        for name, f in self.schema.fields.items():
            for k, f in self._parsing_iterator(name, f):
                d = result
                v = data.get(self.prefix + k, "")
                if v == "" and (f.required or not isinstance(f, fields.String)):
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

    def validate(self, data=None, cleansing=True):
        self.deserialize(data=data, cleansing=True)
        return not self.has_errors()

    def load(self, data=None, cleansing=True):
        data = data or self.rawdata
        if cleansing:
            data = self.cleansing(data)
            self.rawdata = data  # xxx
        return self.schema.load(data)

    def deserialize(self, data=None, cleansing=True):
        result = self.load(data=data, cleansing=cleansing)
        self.errors = result.errors
        self.data = result.data
        return result.data

    def dump(self, data=None):
        data = data or self.data
        result = self.schema.dump(data, update_fields=self._update_fields_option)
        return result

    def serialize(self, data=None):
        result = self.dump(data=data)
        if result.errors:
            raise MarshallingError(result.errors)
        return result.data

    def __getitem__(self, k):
        return self.itemgetter(self.metadata, k)

Form = FormMeta("Form", (FormBase, ), {})


# factories
def form_factory(name, schema, base=FormBase, metaclass=FormMeta, attrs=None, meta=object()):
    return metaclass.from_schema(name, schema, (base, ), attrs or {}, meta=meta)


# TODO:
class ModelForm(Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        super(ModelForm, self).__init__(*args, **kwargs)


def field_factory(marshmallow_field, **options):
    if "required" not in options:
        options["required"] = True
    return partial(field, marshmallow_field, **options)


def select_wrap(pairs, *args, **kwargs):
    choices = [p[0] for p in pairs]
    kwargs["pairs"] = pairs
    return fields.Select(choices, *args, **kwargs)


def nested_wrap(formclass, *args, **kwargs):
    schema = formclass.Schema
    kwargs.update(kwargs.pop("overrides", {}))
    return fields.Nested(schema, *args, **kwargs)


if __name__ != "__main__":
    Nested = field_factory(nested_wrap)
    Any = field_factory(fields.Field)
    Price = field_factory(fields.Price)
    Arbitrary = field_factory(fields.Arbitrary)
    Decimal = field_factory(fields.Decimal)
    DateTime = field_factory(fields.DateTime)
    URL = field_factory(fields.URL)
    Time = field_factory(fields.Time)
    Str = field_factory(fields.Str)
    Bool = field_factory(fields.Bool)
    String = field_factory(fields.String)
    Url = field_factory(fields.Url)
    LocalDateTime = field_factory(fields.LocalDateTime)
    Float = field_factory(fields.Float)
    Email = field_factory(fields.Email)
    Date = field_factory(fields.Date)
    Int = field_factory(fields.Int)
    TimeDelta = field_factory(fields.TimeDelta)
    UUID = field_factory(fields.UUID)
    Function = field_factory(fields.Function)
    FormattedString = field_factory(fields.FormattedString)
    Number = field_factory(fields.Number)
    Method = field_factory(fields.Method)
    Raw = field_factory(fields.Raw)
    Select = field_factory(select_wrap)
    Fixed = field_factory(fields.Fixed)
    QuerySelect = field_factory(fields.QuerySelect)
    ValidatedField = field_factory(fields.ValidatedField)
    Integer = field_factory(fields.Integer)
    QuerySelectList = field_factory(fields.QuerySelectList)
    Boolean = field_factory(fields.Boolean)
    List = field_factory(fields.List)
