# -*- coding:utf-8 -*-
import marshmallow_form as mf


class DateTriple(mf.Form):
    year = mf.Int()
    month = mf.Int()
    day = mf.Int()


class PersonForm(mf.Form):
    name = mf.String()
    age = mf.String()
    birth = mf.Nested(DateTriple)

    class Meta:
        layout = mf.Layout([
            mf.LColumn("name", widget="default"),
            mf.LColumn("age", widget="default"),
            mf.LColumn("birth.year", "birth.month", "birth.day", widget="date"),
        ])


def render(widget, fields):
    if widget == "default":
        for f in fields:
            print("{}: {}".format(f.name, f.value))
    elif widget == "date":
        from datetime import date
        print(date(fields[0].value, fields[1].value, fields[2].value))

data = {"name": "foo", "age": 10, "birth": {"year": 2000, "month": 11, "day": 1}}
form = PersonForm(initial=data)

for lcol, fields in form:
    render(lcol["widget"], fields)
# name: foo
# age: 10
# 2000-11-01
