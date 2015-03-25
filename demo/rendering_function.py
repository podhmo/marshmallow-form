# -*- coding:utf-8 -*-
import marshmallow_form as mf


def input_tag(self):
    fmt = '<input name="{self.name}" type="{type}" value="{self.value}">'
    return fmt.format(self=self, type=self["type"])


class PersonForm(mf.Form):
    name = mf.String(__call__=input_tag, type="text")
    age = mf.Int(__call__=input_tag, type="number")


form = PersonForm(initial={"name": "foo", "age": 0})
print(form.name())
# <input name="name" type="text" value="foo">
print(form.age())
# <input name="age" type="number" value="0">

########################################
# define your custome data type
########################################
from functools import partial


String = partial(mf.String, type="text", __call__=input_tag)
Int = partial(mf.Int, type="number", __call__=input_tag)


class PersonForm(mf.Form):
    name = String()
    age = Int()

form = PersonForm(initial={"name": "foo", "age": 0})
print(form.name())
# <input name="name" type="text" value="foo">
print(form.age())
# <input name="age" type="number" value="0">

