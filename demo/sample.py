import marshmallow_form as mf


class PersonForm(mf.Form):
    name = mf.String(label="名前", placeholder="foo")
    age = mf.Integer(label="年齢", placeholder="0")


class ParentsForm(mf.Form):
    father = mf.Nested(PersonForm, label="父親")
    mother = mf.Nested(PersonForm, label="母親")

# TODO: more gentle sample.
form = PersonForm(initial={"name": "Foo"})
print(form.name["placeholder"])
print(form.name.value)
for f in form:
    print(f.name, f.value)

form = PersonForm({"name": "foo", "age": "a"})
print(form.deserialize())
print(form.errors)

form = ParentsForm()
for f in form:
    print(f.name, f.value)
