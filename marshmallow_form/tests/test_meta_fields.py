# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("marshmallow_form:Form")
class Tests(unittest.TestCase):
    def test_it(self):
        from datetime import datetime

        class PersonForm(self._getTarget()):
            class Meta:
                fields = ("name", "age", "ctime")

        from collections import namedtuple
        Person = namedtuple("Person", "name age ctime")

        person = Person(name="foo", age=10, ctime=datetime(2000, 1, 1))
        form = PersonForm.from_object(person)

        result = [(f.name, f.value) for f in form]
        expected = [('name', 'foo'), ('age', 10), ('ctime', '2000-01-01T00:00:00+00:00')]
        self.assertEqual(result, expected)
