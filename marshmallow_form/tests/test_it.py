# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class RenderingTests(unittest.TestCase):
    def _makeOne(self):
        import marshmallow_form as mf

        class PersonForm(self._getTarget()):
            name = mf.String(doc="名前")
            age = mf.Integer()
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

    def test_add_field(self):
        import marshmallow_form as mf
        form = self._makeOne()()
        form.add_field("birth", mf.Date(required=True, doc="生まれ"))
        self.assertEqual(form.birth["doc"], "生まれ")

    def test_add_field__no_effect_at_other_instance(self):
        import marshmallow_form as mf
        form = self._makeOne()()
        form.add_field("birth", mf.Date(required=True, doc="生まれ"))
        other = self._makeOne()()
        with self.assertRaises(AttributeError):
            other.birth

    def test_remove_field(self):
        form = self._makeOne()()
        form.remove_field("age")
        result = list(f.name for f in form)
        self.assertEqual(result, ["name"])

    def test_remove_field__no_effect_at_other_instance(self):
        form = self._makeOne()()
        form.remove_field("age")

        other = self._makeOne()()
        result = list(f.name for f in other)
        self.assertEqual(result, ["name", "age"])

    def test_choices(self):
        import marshmallow_form as mf
        from collections import namedtuple
        Point = namedtuple("Point", "id value")
        itr = (Point(i, i * 10) for i in range(1, 4))
        query = lambda: itr
        form = self._makeOne()()
        form.add_field("points", mf.QuerySelect(query, lambda o: o.id))
        expected = [(1, 'Point(id=1, value=10)'), (2, 'Point(id=2, value=20)'), (3, 'Point(id=3, value=30)')]
        result = list(form.points.choices)
        self.assertEqual(result, expected)
        result2 = list(form.points.choices)
        self.assertEqual(result2, expected)


@test_target("marshmallow_form:Form")
class ValidationTests(unittest.TestCase):
    def _makeOne(self):
        import marshmallow_form as mf

        class PersonForm(self._getTarget()):
            name = mf.String(doc="名前")
            age = mf.Integer()
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
