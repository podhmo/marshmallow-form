# -*- coding:utf-8 -*-
import unittest
from evilunit import test_function


@test_function("marshmallow_form:form_factory")
class FactoryTests(unittest.TestCase):
    def test_it(self):
        from marshmallow import Schema, fields

        class PersonSchema(Schema):
            name = fields.String()
            age = fields.Int()

            class Meta:
                ordered = True

        Form = self._callFUT("PersonForm", PersonSchema)
        form = Form(initial={"name": "foo", "age": 10})
        result = {f.name: f.value for f in form}
        expected = {"name": "foo", "age": 10}
        self.assertEqual(result, expected)

    def test_validation(self):
        from marshmallow import Schema, fields

        class LoginSchema(Schema):
            name = fields.Str()
            password = fields.Str()
            password_confirm = fields.Str()

        @LoginSchema.validator
        def confirm_password(self, data):
            return data["password"] == data["password_confirm"]

        Form = self._callFUT("LoginForm", LoginSchema)
        assert Form.Schema == LoginSchema
        form = Form({"name": "foo", "password": "*", "password_confirm": "+"})
        self.assertFalse(form.validate())

    def test_with_nested(self):
        from marshmallow import Schema, fields

        class DateTriple(Schema):
            year = fields.Int()
            month = fields.Int()
            day = fields.Int()

            class Meta:
                ordered = True

        class FileSchema(Schema):
            name = fields.String()
            ctime = fields.Nested(DateTriple)

            class Meta:
                ordered = True

        Form = self._callFUT("FileForm", FileSchema)
        form = Form(initial={"name": "foo.txt", "ctime": {"year": 2000, "month": 1, "day": 1}})
        result = {f.name: f.value for f in form}
        expected = {"name": "foo.txt", "ctime.year": 2000, "ctime.month": 1, "ctime.day": 1}
        self.assertEqual(result, expected)
