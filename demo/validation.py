# -*- coding:utf-8 -*-
from datetime import date
from marshmallow import Schema, fields, ValidationError


class DateTriple(Schema):
    year = fields.Int()
    month = fields.Int()
    day = fields.Int()

    def make_object(self, data):
        try:
            return date(**data)
        except:
            return None


@DateTriple.validator
def datecheck(self, data):
        try:
            date(**data)
        except:
            raise ValidationError("invalid paramaters: {}".format(data))


class FileSchema(Schema):
    name = fields.String()
    ctime = fields.Nested(DateTriple)

input_data = {
    "name": "foo.txt",
    "ctime": {
        "year": "2000",
        "month": "@@",
        "day": "99"
    }
}

schema = FileSchema()
data, errors = schema.load(input_data)
# {'name': 'foo.txt', 'ctime': None}
# {
#     'ctime': {
#         'month': ["invalid literal for int() with base 10: '@@'"],
#         '_schema': ["invalid paramaters: OrderedDict([('year', 2000), ('month', None), ('day', 99)])"]
#     }
# }


## Form
from datetime import date
import marshmallow_form as mf


class DateTriple(mf.Form):
    year = mf.Int()
    month = mf.Int()
    day = mf.Int()

    def make_object(self, data):
        try:
            return date(**data)
        except:
            return None

    @mf.Form.validator
    def datecheck(self, data):
        try:
            date(**data)
        except:
            raise ValidationError("invalid paramaters: {}".format(data))


class FileForm(mf.Form):
    name = mf.String()
    ctime = mf.Nested(DateTriple)

input_data = {
    "name": "foo.txt",
    "ctime.year": "2000",
    "ctime.month": "@@",
    "ctime.day": "99"
}

form = FileForm(input_data)
print(form.validate())
print(form.errors)
for f in form:
    print(f.name, f.value)
# name foo.txt
# ctime.year 2000
# ctime.month @@
# ctime.day 99


print(form.ctime.month.errors)
# ["invalid literal for int() with base 10: '@@'"]

print(form.ctime.errors)
# ["invalid paramaters: OrderedDict([('year', 2000), ('month', None), ('day', 99)])"]
