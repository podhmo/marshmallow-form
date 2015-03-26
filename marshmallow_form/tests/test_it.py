# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class RenderingTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        import marshmallow_form as mf

        def input_tag(self):
            return '<input name="{self.name}" value="{self.value}">'.format(self=self)

        class PersonForm(self._getTarget()):
            name = mf.String(doc="名前", __call__=input_tag)
            age = mf.Integer()
        return PersonForm(*args, **kwargs)

    def test_accessing_metadata(self):
        form = self._makeOne()
        self.assertEqual(form.name["doc"], "名前")

    def test_accessing_value__initial(self):
        form = self._makeOne(initial={"name": "foo"})
        self.assertEqual(form.name.value, "foo")

    def test_accessing_value(self):
        form = self._makeOne({"name": "foo"})
        self.assertEqual(form.name.value, "foo")

    def test_define_call_method(self):
        form = self._makeOne({"name": "foo"})
        self.assertEqual(form.name(), '<input name="name" value="foo">')

    def test_iterate_order(self):
        form = self._makeOne()
        result = list(f.name for f in form)
        self.assertEqual(result, ["name", "age"])

    def test_modify_metadata__no_effect_at_other_instance(self):
        form = self._makeOne()
        form.name.metadata["class"] = "js-name"
        self.assertIn("class", form.name.metadata)
        other = self._makeOne()
        self.assertNotIn("class", other.name.metadata)

    def test_add_field(self):
        import marshmallow_form as mf
        form = self._makeOne()
        form.add_field("birth", mf.Date(required=True, doc="生まれ"))
        self.assertEqual(form.birth["doc"], "生まれ")

    def test_add_field__no_effect_at_other_instance(self):
        import marshmallow_form as mf
        form = self._makeOne()
        form.add_field("birth", mf.Date(required=True, doc="生まれ"))
        other = self._makeOne()
        with self.assertRaises(AttributeError):
            other.birth

    def test_remove_field(self):
        form = self._makeOne()
        form.remove_field("age")
        result = list(f.name for f in form)
        self.assertEqual(result, ["name"])

    def test_remove_field__no_effect_at_other_instance(self):
        form = self._makeOne()
        form.remove_field("age")

        other = self._makeOne()
        result = list(f.name for f in other)
        self.assertEqual(result, ["name", "age"])

    def test_choices(self):
        import marshmallow_form as mf
        from collections import namedtuple
        Point = namedtuple("Point", "id value")
        itr = (Point(i, i * 10) for i in range(1, 4))
        query = lambda: itr
        form = self._makeOne()
        form.add_field("points", mf.QuerySelect(query, lambda o: o.id))
        expected = [(1, 'Point(id=1, value=10)'), (2, 'Point(id=2, value=20)'), (3, 'Point(id=3, value=30)')]
        result = list(form.points.choices)
        self.assertEqual(result, expected)
        result2 = list(form.points.choices)
        self.assertEqual(result2, expected)


@test_target("marshmallow_form:Form")
class FromObjectTests(unittest.TestCase):
    def test_it(self):
        import marshmallow_form as mf
        from datetime import date
        Class = self._getTarget()

        class Form(Class):
            name = mf.String()
            birth = mf.Date()

        form = Form.from_object({"name": "foo", "birth": date(2000, 1, 1)})
        self.assertEqual(form.birth.value, "2000-01-01")

    def test_it2(self):
        import marshmallow_form as mf
        from datetime import date
        from collections import namedtuple
        Person = namedtuple("Person", "name birth")

        Class = self._getTarget()

        class Form(Class):
            name = mf.String()
            birth = mf.Date()

        form = Form.from_object(Person(name="foo", birth=date(2000, 1, 1)))
        self.assertEqual(form.birth.value, "2000-01-01")

        form = Form({"name": "foo", "birth": "2000-01-01"})
        result = form.deserialize()
        expected = {"name": "foo", "birth": date(2000, 1, 1)}
        self.assertEqual(result, expected)


@test_target("marshmallow_form:Form")
class InheritanceTests(unittest.TestCase):
    def test_it(self):
        import marshmallow_form as mf
        Class = self._getTarget()

        class Base(Class):
            name = mf.String()

        class Inherited(Base):
            age = mf.Int()

        form = Inherited()
        result = [f.name for f in form]
        expected = ["name", "age"]
        self.assertEqual(result, expected)

    def test_it2(self):
        import marshmallow_form as mf
        Class = self._getTarget()

        class Base(Class):
            name = mf.String(doc="base")

        class Inherited(Base):
            name = mf.Int(doc="inherited")
            age = mf.Int()

        form = Inherited()
        result = [f.name for f in form]
        expected = ["name", "age"]
        self.assertEqual(result, expected)
        self.assertEqual(form.name["doc"], "inherited")

    def test_it3(self):
        import marshmallow_form as mf
        Class = self._getTarget()

        class Name(Class):
            name = mf.String()

        class Age(Class):
            age = mf.Int()

        class Date(Class):
            year = mf.Int()
            month = mf.Int()
            day = mf.Int()

        class CTime(Class):
            ctime = mf.Nested(Date)

        class UTime(Class):
            utime = mf.Nested(Date)

        class Inherited(Name, Age, CTime, UTime):
            pass

        form = Inherited()
        result = [f.name for f in form]
        expected = ["name", "age", "ctime.year", "ctime.month", "ctime.day", "utime.year", "utime.month", "utime.day"]
        self.assertEqual(result, expected)

    def test_validator(self):
        Class = self._getTarget()
        marker = object()
        r = []

        class Base(Class):
            @Class.validator
            def validate(self, data):
                r.append(marker)

        class Inherited(Base):
            pass

        form = Inherited()
        form.deserialize({})
        self.assertEqual(r, [marker])


@test_target("marshmallow_form:Form")
class MetaDataTests(unittest.TestCase):
    def _makeField(self, *args, **kwargs):
        import marshmallow_form as mf
        return mf.String(*args, **kwargs)

    def _makeNested(self, *args, **kwargs):
        import marshmallow_form as mf
        return mf.Nested(*args, **kwargs)

    def test_field_missing(self):
        Class = self._getTarget()

        class Form(Class):
            name = self._makeField()
        form = Form()
        self.assertEqual(form.name["doc"], "")

    def test_field(self):
        Class = self._getTarget()

        class Form(Class):
            name = self._makeField(doc="this is name")
        form = Form()
        self.assertEqual(form.name["doc"], "this is name")

    def test_field_nested(self):
        Class = self._getTarget()

        class Named(Class):
            name = self._makeField(doc="this is name")

        class Form(Class):
            box = self._makeNested(Named)
        form = Form()
        self.assertEqual(form.box.name["doc"], "this is name")

    def test_field_nested__overrides(self):
        Class = self._getTarget()

        class Named(Class):
            name = self._makeField(doc="this is name")

        class Form(Class):
            box = self._makeNested(Named, overrides={"name": {"doc": "this is box name"}})
        form = Form()
        self.assertEqual(form.box.name["doc"], "this is box name")

    def test_field_inheritance(self):
        Class = self._getTarget()

        class Named(Class):
            name = self._makeField(doc="this is name")

        class Form(Named):
            pass
        form = Form()
        self.assertEqual(form.name["doc"], "this is name")

    def test_field_inheritance_overrides(self):
        Class = self._getTarget()

        class Named(Class):
            name = self._makeField(doc="this is name")

        class Form(Named):
            class Meta:
                overrides = {"name": {"doc": "*this is name*"}}
        form = Form()
        self.assertEqual(form.name["doc"], "*this is name*")

    def test_form(self):
        Class = self._getTarget()

        class Form(Class):
            class Meta:
                metadata = {"doc": "this is form"}
        form = Form()
        self.assertEqual(form["doc"], "this is form")

    def test_form_inheritance(self):
        Class = self._getTarget()

        class Base(Class):
            class Meta:
                metadata = {"doc": "this is base"}

        class Form(Base):
            pass

        form = Form()
        self.assertEqual(form["doc"], "this is base")

    def test_form_inheritance_overrides(self):
        Class = self._getTarget()

        class Base(Class):
            class Meta:
                metadata = {"doc": "this is base"}

        class Form(Base):
            class Meta:
                metadata = {"doc": "this is form"}

        form = Form()
        self.assertEqual(form["doc"], "this is form")

    def test_change_itemgetter(self):
        Class = self._getTarget()

        class Form(Class):
            name = self._makeField()

            class Meta:
                itemgetter = lambda d, k: d[k]

        form = Form()
        with self.assertRaises(KeyError):
            form.name["doc"]


@test_target("marshmallow_form:Form")
class NestedTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from collections import namedtuple
        import marshmallow_form as mf
        Class = self._getTarget()

        self.Person = Person = namedtuple("Person", "name age")

        class PersonForm(Class):
            name = mf.String()
            age = mf.Int()

            def make_object(self, kwargs):
                return Person(**kwargs)

        class ParentsForm(Class):
            yagou = mf.String()
            father = mf.Nested(PersonForm)
            mother = mf.Nested(PersonForm)
        return ParentsForm(*args, **kwargs)

    def test_cleansing(self):
        form = self._makeOne()
        input_data = {
            "yagou": "bar",
            "father.name": "foo",
            "father.age": "10",
            "mother.name": "foo",
            "mother.age": "10",
        }
        result = form.cleansing(input_data)
        expected = {
            "yagou": "bar",
            "father": {
                "name": "foo",
                "age": "10"
            },
            "mother": {
                "name": "foo",
                "age": "10"
            }
        }
        self.assertEqual(result, expected)

    def test_deserialize(self):
        form = self._makeOne()
        user_data = {"name": "foo", "age": "10"}
        input_data = {"yagou": "bar",
                      "father": user_data,
                      "mother": user_data}
        result = form.deserialize(input_data, cleansing=False)
        expected = {
            "mother": self.Person("foo", 10),
            "father": self.Person("foo", 10),
            "yagou": "bar"
        }
        self.assertEqual(result, expected)

    def test_serialize(self):
        form = self._makeOne()
        result = {f.name: f.value for f in form}
        expected = {
            'father.age': 0,
            'mother.name': '',
            'yagou': '',
            'father.name': '',
            'mother.age': 0
        }
        self.assertEqual(result, expected)

    def test_initial(self):
        initial_data = {
            "mother": {"name": "foo", "age": 10},
            "father": {"name": "foo", "age": 10},
            "yagou": "bar"
        }
        form = self._makeOne(initial=initial_data)
        result = {f.name: f.value for f in form}
        expected = {
            'yagou': 'bar',
            'mother.age': 10,
            'father.name': 'foo',
            'mother.name': 'foo',
            'father.age': 10
        }
        self.assertEqual(result, expected)
        self.assertEqual(form.father.name.value, "foo")


@test_target("marshmallow_form:Form")
class NestedTests2(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        import marshmallow_form as mf
        Class = self._getTarget()

        class X(Class):
            name = mf.String(required=False)

        class Y(Class):
            x0 = mf.Nested(X)
            x1 = mf.Nested(X)

        class Z(Class):
            y0 = mf.Nested(Y)
            y1 = mf.Nested(Y)
        return Z(*args, **kwargs)

    def test_it(self):
        form = self._makeOne()
        input_data = {f.name: f.value for f in form}
        result = form.deserialize(input_data)
        expected = {'y0': {'x1': {'name': ''},
                           'x0': {'name': ''}},
                    'y1': {'x1': {'name': ''},
                           'x0': {'name': ''}}}
        self.assertEqual(result, expected)
