# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class SimpleTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        import marshmallow_form as mf

        class PersonForm(self._getTarget()):
            name = mf.String(doc="名前")
            age = mf.Integer()
        return PersonForm(*args, **kwargs)

    def test_success(self):
        input_data = {"name": "foo", "age": "10"}
        form = self._makeOne(input_data)
        result = form.deserialize()
        self.assertEqual(result, {"name": "foo", "age": 10})

    def test_failure__missing(self):
        input_data = {"name": "foo"}
        form = self._makeOne(input_data)
        form.deserialize()
        self.assertTrue(form.has_errors())
        self.assertEqual(list(form.errors.keys()), ["age"])

    def test_failure__invalid(self):
        input_data = {"name": "foo", "age": "@@"}
        form = self._makeOne(input_data)
        form.deserialize()
        self.assertTrue(form.has_errors())
        self.assertEqual(list(form.errors.keys()), ["age"])

    def test_with_prefix(self):
        input_data = {"foo-name": "foo", "foo-age": "10"}
        form = self._makeOne(input_data, prefix="foo-")
        result = form.deserialize()
        self.assertFalse(form.has_errors())
        self.assertEqual(result, {"name": "foo", "age": 10})

    def test_with_errors_access(self):
        input_data = {"name": "foo", "age": "@@"}
        form = self._makeOne(input_data)
        form.deserialize()
        self.assertTrue(form.has_errors())
        self.assertTrue(form.age.errors)
        self.assertEqual(form.name.value, "foo")
        self.assertEqual(form.age.value, "@@")


@test_target("marshmallow_form:Form")
class NestedTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from datetime import date
        import marshmallow_form as mf

        class DateTriple(self._getTarget()):
            year = mf.Int()
            month = mf.Int()
            day = mf.Int()

            def make_object(self, data):
                try:
                    return date(**data)
                except:
                    return data

        class FileForm(self._getTarget()):
            name = mf.String()
            ctime = mf.Nested(DateTriple)
        return FileForm(*args, **kwargs)

    def test_success(self):
        from datetime import date
        input_data = {"name": "foo", "ctime.year": "2000", "ctime.month": "1", "ctime.day": "1"}
        form = self._makeOne(input_data)
        result = form.deserialize()
        expected = {"name": "foo", "ctime": date(2000, 1, 1)}
        self.assertEqual(expected, result)

    def test_with_errors_access(self):
        input_data = {"name": "foo", "ctime.year": "@@", "ctime.month": "1", "ctime.day": "1"}
        form = self._makeOne(input_data)
        self.assertFalse(form.validate())
        self.assertTrue(form.ctime.year.errors)

        self.assertEqual(form.name.value, "foo")
        self.assertEqual(form.ctime.year.value, "@@")  # default
        self.assertEqual(form.ctime.month.value, "1")  # default
