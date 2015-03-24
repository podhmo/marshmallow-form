import marshmallow_form as mf


class PersonForm(mf.Form):
    name = mf.String(label="名前", placeholder="foo", widget="str")
    age = mf.Integer(label="年齢", placeholder="0", widget="int")


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


from mako.template import Template

template = Template("""
<%def name="field(f)">\
  ${getattr(self, "field_" + f["widget"])(f)}
</%def>

<%def name="field_str(f)">\
  <input type="text" name="${f.name}" value="${f.value}" placeholder="${f["placeholder"]}"/>
</%def>

<%def name="field_int(f)">\
  <input type="number" name="${f.name}" value="${f.value}" placeholder="${f["placeholder"]}"/>
</%def>

<form action="#" method="POST">
%for f in form:
${field(f)}
%endfor
</form>
""")

print(template.render(form=form))
