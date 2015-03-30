# -*- coding:utf-8 -*-
import marshmallow_form as mf

from collections import namedtuple
Person = namedtuple("Person", "name age")


class PersonForm(mf.Form):
    name = mf.Str()
    age = mf.Int()

    def make_object(self, data):
        return Person(**data)


PersonForm.Schema  # => <class 'marshmallow.schema.PersonSchema'>
schema = PersonForm.Schema(many=True)
schema.dump([Person("foo", 20), Person("bar", 20)]).data
# => OrderedDict([('name', 'foo'), ('age', 20)]), OrderedDict([('name', 'bar'), ('age', 20)])

form = PersonForm()
form.schema.load({"name": "foo", "age": 20}).data  # => Person(name='foo', age=20)
