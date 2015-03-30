# -*- coding:utf-8 -*-
import marshmallow_form as mf


class MyForm(mf.Form):
    name = mf.Str()

    class Meta:
        metadata = {"action": "#"}

form = MyForm()
form["action"]  # => #
form.metadata["method"] = "post"
form["method"]  # => "post"

MyForm()["method"]  # => ""


class MyForm2(mf.Form):
    name = mf.Str()
    ctime = mf.DateTime(disable=True)


form = MyForm2()
form.ctime["disable"]  # => True


from functools import partial
DateTime = partial(mf.DateTime, widget="tdcalendar")


class MyForm3(mf.Form):
    ctime = DateTime()
    utime = DateTime()

form = MyForm3()
form.ctime["widget"]  # => tdcalendar
form.utime["widget"]  # => tdcalendar


class MyForm4(MyForm3):
    class Meta:
        overrides = {"ctime": {"widget": "mycalendar"}}


form = MyForm4()
form.ctime["widget"]  # => mycalendar
form.utime["widget"]  # => tdcalendar


class PersonForm(mf.Form):
    name = mf.String(label="名前", placeholder="foo", widget="str")
    age = mf.Integer(label="年齢", placeholder="0", widget="int")


class ParentsForm(mf.Form):
    father = mf.Nested(PersonForm, label="父親", overrides={"name": {"label": "父親の名前"}})
    mother = mf.Nested(PersonForm, label="母親")

form = ParentsForm()
form.father["label"]  # => "父親"
form.father.name["label"]  # => "父親の名前"
