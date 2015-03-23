# -*- coding:utf-8 -*-
import marshmallow_form as mf


class PersonForm(mf.Form):
    name = mf.String()
    age = mf.Int()


class StudentForm(PersonForm):
    grade = mf.String()


form = StudentForm(initial={"name": "foo", "age": 10, "grade": 4})
for f in form:
    print(f.name, f.value)
# name foo
# age 10
# grade 4
