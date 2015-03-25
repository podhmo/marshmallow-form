# -*- coding:utf-8 -*-
import unittest


def transcribe(target):
    from marshmallow_form import Form
    from marshmallow_form.boundfield import BoundField
    from marshmallow_form.layout import LColumn
    if isinstance(target, BoundField):
        return target.name
    if isinstance(target, Form):
        return [transcribe(row) for row in target]
    elif isinstance(target, (list, tuple)):
        if isinstance(target[0], LColumn):
            lcolumn, fields = target
            return "{}:({})".format(lcolumn["widget"], ", ".join([transcribe(field) for field in fields]))
        else:
            return [transcribe(row) for row in target]
    else:
        raise Exception("oops")


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
        from marshmallow_form.layout import Layout, LColumn

        class LayoutedForm(self._makeBase()):
            class Meta:
                layout = Layout([
                    LColumn("info.tel", "info.zip", widget="row"),
                    LColumn("info.address.country",
                            "info.address.prefecture",
                            "info.address.city",
                            "info.address.street", widget="row"),
                    (LColumn("father.name", "father.age", widget="person"),
                     LColumn("mother.name", "mother.age", widget="person"))
                ])
        form = LayoutedForm()
        result = transcribe(form)
        expected = [
            'row:(info.tel, info.zip)',
            'row:(info.address.country, info.address.prefecture, info.address.city, info.address.street)',
            ['person:(father.name, father.age)', 'person:(mother.name, mother.age)']
        ]
        self.assertEqual(result, expected)

    def test_layout__too_few(self):
        from marshmallow_form.layout import Layout, LayoutTooFew
        with self.assertRaises(LayoutTooFew):
            class LayoutedForm(self._makeBase()):
                class Meta:
                    layout = Layout([])

    def test_layout__too_many(self):
        from marshmallow_form.layout import Layout, LayoutTooMany, LColumn
        with self.assertRaises(LayoutTooMany):
            class LayoutedForm(self._makeBase()):
                class Meta:
                    layout = Layout([
                        LColumn("aaaa", widget="row"),
                        LColumn("info.tel", "info.zip", widget="row"),
                        LColumn("info.address.country",
                                "info.address.prefecture",
                                "info.address.city",
                                "info.address.street", widget="row"),
                        (LColumn("father.name", "father.age", widget="person"),
                         LColumn("mother.name", "mother.age", widget="person"))
                    ])
