# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class RegressionTests(unittest.TestCase):
    def test_13(self):
        """Cannot have multiple levels of nesting -- with validation"""
        # https://github.com/podhmo/marshmallow-form/issues/13
        import marshmallow_form as mf
        Class = self._getTarget()

        class HasNameForm(Class):
            name = mf.String()

        class PairNameForm(Class):
            left = mf.Nested(HasNameForm)
            right = mf.Nested(HasNameForm)

        class PastPresentFutureForm(Class):
            past = mf.Nested(PairNameForm)
            present = mf.Nested(PairNameForm)
            future = mf.Nested(PairNameForm)

        form = PastPresentFutureForm({})
        self.assertFalse(form.validate())
        list(form)

