# -*- coding:utf-8 -*-
# see: http://marshmallow.readthedocs.org/en/latest/extending.html
import marshmallow_form as mf
from marshmallow.validate import Length

########################################
# error handler
########################################


class Form(mf.Form):
    name = mf.String(validate=Length(10))

    @mf.Form.error_handler
    def handle_errors(schema, errors, obj):
        raise Exception(errors)


form = Form({"name": "*"})
# print(form.deserialize())
# Exception: {'name': ['Shorter than minimum length 10.']}


########################################
# post_process
########################################

class DateTriples(mf.Form):
    year = mf.Int()
    month = mf.Int()
    day = mf.Int()

    def make_object(self, data):
        from datetime import date
        return date(data["year"], data["month"], data["day"])


class Form2(mf.Form):
    utime = mf.Nested(DateTriples)

form = Form2({"utime.year": "2000", "utime.month": "2", "utime.day": "1"})
print(form.deserialize())
# OrderedDict([('utime', datetime.date(2000, 2, 1))])


########################################
# pre_process
########################################

class Form(mf.Form):
    name = mf.String(required=False)

    @mf.Form.preprocessor
    def case_insensitive(self, data):
        data["name"] = data["name"].lower()
        return data

form = Form({"name": "Foo"})
print(form.deserialize())
# OrderedDict([('name', 'foo')])

form = Form({})
print(form.deserialize())
# OrderedDict([('name', '')])


########################################
# pre_process
########################################
import marshmallow_form as mf
from datetime import date
from collections import namedtuple
Person = namedtuple("Person", "name birth")


class PersonForm(mf.Form):
    name = mf.String()
    birth = mf.Date()

    @mf.Form.accessor
    def access(self, k, ob):
        return getattr(ob, k)

person = Person(name="foo", birth=date(2000, 1, 1))
form = PersonForm.from_object(person)
print(type(form.birth.value), form.birth.value)
# <class 'str'> 2000-01-01
