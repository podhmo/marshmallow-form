# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class RenderingTests(unittest.TestCase):
    def _makeOne(self):
        import marshmallow_form as mf

        class PersonForm(self._getTarget()):
            name = mf.StringField(doc="名前")
            age = mf.IntegerField()
        return PersonForm

    def test_accessing_metadata(self):
        form = self._makeOne()()
        self.assertEqual(form.name["doc"], "名前")

    def test_accessing_value__initial(self):
        form = self._makeOne()(initial={"name": "foo"})
        self.assertEqual(form.name.value, "foo")

    def test_accessing_value(self):
        form = self._makeOne()({"name": "foo"})
        self.assertEqual(form.name.value, "foo")

    def test_iterate_order(self):
        form = self._makeOne()()
        result = list(f.name for f in form)
        self.assertEqual(result, ["name", "age"])


@test_target("marshmallow_form:Form")
class ValidationTests(unittest.TestCase):
    def _makeOne(self):
        import marshmallow_form as mf

        class PersonForm(self._getTarget()):
            name = mf.StringField(doc="名前")
            age = mf.IntegerField()
        return PersonForm

    def test_success(self):
        input_data = {"name": "foo", "age": "10"}
        form = self._makeOne()(input_data)
        result = form.deserialize()
        self.assertEqual(result, {"name": "foo", "age": 10})

    def test_failure__missing(self):
        input_data = {"name": "foo"}
        form = self._makeOne()(input_data)
        form.deserialize()
        self.assertTrue(form.has_errors())
        self.assertEqual(list(form.errors.keys()), ["age"])

    def test_failure__invalid(self):
        input_data = {"name": "foo", "age": "@@"}
        form = self._makeOne()(input_data)
        form.deserialize()
        self.assertTrue(form.has_errors())
        self.assertEqual(list(form.errors.keys()), ["age"])

    def test_with_prefix(self):
        input_data = {"foo-name": "foo", "foo-age": "10"}
        form = self._makeOne()(input_data, prefix="foo-")
        result = form.deserialize()
        self.assertFalse(form.has_errors())
        self.assertEqual(result, {"name": "foo", "age": 10})
