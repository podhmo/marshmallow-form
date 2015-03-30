import marshmallow_form as mf
import functools
PositiveInt = functools.partial(mf.Int, validate=lambda x: x > 0)


class Form(mf.Form):
    x = PositiveInt()

print(Form({"x": "-10"}).load())
# UnmarshalResult(data=OrderedDict([('x', None)]), errors={'x': ['Validator <lambda>(-10) is False']})


from marshmallow.fields import Field
from marshmallow.exceptions import UnmarshallingError
import base64


class Base64(Field):
    """ tiny base64 field"""
    def __init__(self, *args, **kwargs):
        super(Base64, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        return base64.encodebytes(value)

    def _deserialize(self, value):
        try:
            return base64.decodebytes(value.encode("utf-8"))
        except:
            raise UnmarshallingError("oops")

MyBase64 = mf.field_factory(Base64)


class Form(mf.Form):
    x = MyBase64(label="this is broken")

form = Form({"x": "MTEx"})
print(form.load())
# UnmarshalResult(data=OrderedDict([('x', b'111')]), errors={})


def input(field, placeholder=""):
    fmt = '<input name="{name}" value="{value}" placeholder="{placeholder}">'
    return fmt.format(name=field["name"], value=field.value, placeholder=placeholder)


class Form(mf.Form):
    name = mf.Str(__call__=input)

form = Form()
print(form.name(placeholder="foo"))

# => <input name="" value="" placeholder="foo">

