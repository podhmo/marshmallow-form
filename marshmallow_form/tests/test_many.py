# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class Tests(unittest.TestCase):
    def _makeString(self, *args, **kwargs):
        import marshmallow_form as mf
        return mf.String(*args, **kwargs)

    def _makeNested(self, *args, **kwargs):
        import marshmallow_form as mf
        return mf.Nested(*args, **kwargs)

    @unittest.skip("not supported")
    def test_form_many(self):
        Class = self._getTarget()

        class PersonForm(Class):
            name = self._makeString()

        class person0:
            name = "foo"

        class person1:
            name = "bar"

        class person2:
            name = "boo"
        ob = [person0, person1, person2]
        form = PersonForm.from_object(ob, options={"many": True})
        for c in form:
            print(c)

    def test_field_many(self):
        Class = self._getTarget()

        class Text(Class):
            head = self._makeString()
            body = self._makeString()

        class Form(Class):
            texts = self._makeNested(Text, many=True)

        class Ob:
            class foo:
                head = "^"
                body = "foo"

            class bar:
                head = "^"
                body = "bar"

            texts = [foo, bar]

        form = Form.from_object(Ob)
        self.assertEqual(form.texts[0].body.name, "texts.0.body")
        self.assertEqual(form.texts[0].body.value, "foo")
        self.assertEqual(form.texts[1].body.name, "texts.1.body")
        self.assertEqual(form.texts[1].body.value, "bar")

        result = [(f.name, f.value) for c in form for f in c]
        expected = [
            ("texts.0.head", "^"), ("texts.0.body", "foo"),
            ("texts.1.head", "^"), ("texts.1.body", "bar"),
        ]
        self.assertEqual(result, expected)
