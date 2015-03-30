# -*- coding:utf-8 -*-
import marshmallow_form as mf


class StudentForm(mf.Form):
    color = mf.Select([])
    name = mf.Str()

form = StudentForm()
form.color.metadata["pairs"] = [("red", "red"), ("blue", "blue")]
form.color["pairs"]  # => [('red', 'red'), ('blue', 'blue')]


form = StudentForm(initial={"grade": 3})
form.add_field("grade", mf.Int(label="学年"))
form.grade.value  # => 3
form.grade["label"]  # => "学年"

[f.name for f in form]  # => ['color', 'name', 'grade']


form = StudentForm()
form.remove_field("color")
[f.name for f in form]  # => ['name']
