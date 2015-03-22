import marshmallow_form as mf


class PersonForm(mf.Form):
    name = mf.String(label="名前", placeholder="foo")
    age = mf.Integer(label="年齢", placeholder="0")


class ParentsForm(mf.Form):
    father = mf.Nested(PersonForm.schema_factory)
    mother = mf.Nested(PersonForm.schema_factory)

# print(PersonForm.schema_factory)
# print(PersonForm(options={"many": True}).schema)
form = PersonForm(initial={"name": "Foo"})
print(form.name["placeholder"])
print(form.name.value)
for f in form:
    print(f)

form = PersonForm({"name": "foo", "age": "a"})
print(form.deserialize())
print(form.errors)

# # TODO:nested
# form = ParentsForm()
# for f in form:
#     for sf in f:
#         print(sf)
