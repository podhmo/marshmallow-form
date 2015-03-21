import marshmallow_form as mf


class PersonForm(mf.Form):
    name = mf.StringField(label="名前", placeholder="foo")
    age = mf.IntegerField(label="年齢", placeholder="0")


class ParentsForm(mf.Form):
    father = mf.NestedField(PersonForm.schema_factory)
    mother = mf.NestedField(PersonForm.schema_factory)

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
