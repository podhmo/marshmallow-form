# -*- coding:utf-8 -*-
import marshmallow_form as mf
from marshmallow import ValidationError


class LoginForm(mf.Form):
    name = mf.String()
    password = mf.String()
    password_confirm = mf.String()


@LoginForm.Schema.validator
def same(schema, data):
    return data["password"] == data["password_confirm"]

input_data = {"name": "foo", "password": "*", "password_confirm": "+"}
form = LoginForm(input_data)
form.deserialize()
print(form.errors)
# ["Schema validator same({'password_confirm': '+', 'name': 'foo', 'password': '*'}) is False"]

from marshmallow.validate import Length


class MLength(Length):
    message_min = 'Too short! {min}.'
    message_max = 'Too long! {max}.'


class LoginForm(mf.Form):
    name = mf.String()
    password = mf.String(validate=MLength(5))
    password_confirm = mf.String()

    @mf.Form.validator
    def same(schema, data):
        if data["password"] != data["password_confirm"]:
            raise ValidationError("not same!", "password")


input_data = {"name": "foo", "password": "*", "password_confirm": "+"}
form = LoginForm(input_data)
form.deserialize()
print(form.errors)
{'password': ['Too short! 5.', 'not same!']}
