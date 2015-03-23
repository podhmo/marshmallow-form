# -*- coding:utf-8 -*-
import unittest


def transcribe(target):
    from marshmallow_form import BoundField
    if isinstance(target, BoundField):
        return target.name
    else:
        return [transcribe(row) for row in target]


class LayoutTests(unittest.TestCase):
    def _makeBase(self):
        import marshmallow_form as mf

        class PersonForm(mf.Form):
            name = mf.String()
            age = mf.Int()

        class AddressForm(mf.Form):
            country = mf.String()
            prefecture = mf.String()
            city = mf.String()
            street = mf.String()

        class InformationForm(mf.Form):
            zip = mf.String()
            tel = mf.String()
            address = mf.Nested(AddressForm)

        class FamilyCardForm(mf.Form):
            father = mf.Nested(PersonForm)
            mother = mf.Nested(PersonForm)
            info = mf.Nested(InformationForm)
        return FamilyCardForm

    def test_simple(self):
        class FlattenForm(self._makeBase()):
            pass
        form = FlattenForm()
        result = transcribe(form)
        expected = ['father.name',
                    'father.age',
                    'mother.name',
                    'mother.age',
                    'info.zip',
                    'info.tel',
                    'info.address.country',
                    'info.address.prefecture',
                    'info.address.city',
                    'info.address.street',
                    ]
        self.assertEqual(result, expected)

    def test_layout(self):
        from marshmallow_form import Layout

        class LayoutedForm(self._makeBase()):
            class Meta:
                layout = Layout([
                    ("info.tel", "info.zip"),
                    ("info.address.country", "info.address.prefecture", "info.address.city", "info.address.street"),
                    (("father.name", "father.age"), ("mother.name", "mother.age"))
                ])
        form = LayoutedForm()
        result = transcribe(form)
        expected = [['info.tel', 'info.zip'],
                    ['info.address.country', 'info.address.prefecture', 'info.address.city', 'info.address.street'],
                    [['father.name', 'father.age'], ['mother.name', 'mother.age']]]
        self.assertEqual(result, expected)

    def test_layout__too_few(self):
        from marshmallow_form import Layout, LayoutTooFew
        with self.assertRaises(LayoutTooFew):
            class LayoutedForm(self._makeBase()):
                class Meta:
                    layout = Layout([])

    def test_layout__too_many(self):
        from marshmallow_form import Layout, LayoutTooMany
        with self.assertRaises(LayoutTooMany):
            class LayoutedForm(self._makeBase()):
                class Meta:
                    layout = Layout([
                        ("aaaaa", "bbbb"),
                        ("info.tel", "info.zip"),
                        ("info.address.country", "info.address.prefecture", "info.address.city", "info.address.street"),
                        (("father.name", "father.age"), ("mother.name", "mother.age"))
                    ])
