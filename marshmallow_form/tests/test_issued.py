# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class Issued13Tests(unittest.TestCase):
    """Cannot have multiple levels of nesting -- with validation"""
    # https://github.com/podhmo/marshmallow-form/issues/13

    def _makeForm(self, *args, **kwargs):
        import marshmallow_form as mf
        Class = self._getTarget()

        class HasNameForm(Class):
            name = mf.Int()

        class PairNameForm(Class):
            left = mf.Nested(HasNameForm)
            right = mf.Nested(HasNameForm)

        class PastPresentFutureForm(Class):
            past = mf.Nested(PairNameForm)
            present = mf.Nested(PairNameForm)
            future = mf.Nested(PairNameForm)
        return PastPresentFutureForm(*args, **kwargs)

    def test_13__format_error(self):
        input_data = {
            "past.left.name": object(),
            "past.right.name": "10",
            "present.left.name": object(),
            "present.right.name": "10",
            "future.left.name": object(),
            "future.right.name": "10",
        }
        form = self._makeForm(input_data)
        self.assertFalse(form.validate())
        expected = [["int() argument must be a string or a number, not 'object'"],
                    [],
                    ["int() argument must be a string or a number, not 'object'"],
                    [],
                    ["int() argument must be a string or a number, not 'object'"],
                    []]
        self.assertEqual(list(f.errors for f in form), expected)

    def test_13__missing_value(self):
        input_data = {
            "past.left.name": "10"
        }
        form = self._makeForm(input_data)
        self.assertFalse(form.validate())
        expected = [[],
                    ['Missing data for required field.'],
                    ['Missing data for required field.'],
                    ['Missing data for required field.'],
                    ['Missing data for required field.'],
                    ['Missing data for required field.']]
        self.assertEqual(list(f.fullerrors for f in form), expected)

