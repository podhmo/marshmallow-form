# -*- coding:utf-8 -*-
import marshmallow_form as mf


class DateTriple(mf.Form):
    year = mf.Int(doc="year of date", widget="int")
    month = mf.Int(doc="month of date", widget="int")
    day = mf.Int(doc="day of date", widget="int")

    def make_object(self, data):
        from datetime import date
        return date(data["year"], data["month"], data["day"])


class Form(mf.Form):
    class Meta:
        metadata = {"action": "POST"}

    ctime = mf.Nested(DateTriple, overrides={"year": {"doc": "year of ctime"}})

form = Form()
print(form.ctime.year["doc"])  # year of ctime
print(form.ctime.year["month"])  # year of date


class HasName(mf.Form):
    name = mf.String(doc="name of hasname")
    ctime = mf.Nested(DateTriple)


class Form(HasName):
    class Meta:
        overrides = {
            "name": {"doc": "name of form"},
            "ctime": {"year": {"doc": "year of date of form"}}
        }

form = Form()
print(form.name["doc"])  # name of form
print(form.ctime.year["doc"])  # year of date of form
