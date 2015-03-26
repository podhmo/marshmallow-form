marshmallow-form
========================================

motivation
----------------------------------------

form library is not validation library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What is form library?

- anyone says, 'it is validation library for post/get data'
- another says, 'it is rendering library for form element'

marshmallow-form is not above one.
form library is 'a container for presentation metadata'. so, form object is just a container.

- 'rendering form element', it is a task of template library(mako, jinja2, ...).
- 'validation post/get data', it is a task of schema library(colander, marshmallow, ...).

marshmallow-form is just a metadata container.

getting started
----------------------------------------

install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from pypi package repository.

::

   # pip install marshmallow-form  # sorry, haven't upploaded yet.

from repository

::

   git clone git@github.com/podhmo/marshmallow-form.git
   cd marshmallow-form
   python setup.py develop


form class definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

the way of form definition.

.. code-block:: python

  import marshmallow_form as mf


  class PersonForm(mf.Form):
      name = mf.String(label="名前", placeholder="foo", widget="str")
      age = mf.Integer(label="年齢", placeholder="0", widget="int")


  class ParentsForm(mf.Form):
      father = mf.Nested(PersonForm, label="父親")
      mother = mf.Nested(PersonForm, label="母親")

- define form class with marshmallow_form.Form
- using field classes, define form fields.
- label and placeholder is metadata for presentation


with template library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

with template library, form is just a metadata container.
so, a above definition, using form as metadata container.


.. code-block:: python

  print(form.father.name["label"]) # => '名前'  # 'name' in japanese
  print(form.father.name["placeholder"]) # => 'foo'
  print(form.name.value) # => 'foo'

- accessing metadata with `__getitem__`.
- accessing initial data or passed data with `.value`


with template(mako). deciding rendering method, using `widget` metadata.

.. code-block:: python

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

output.

.. code-block:: html

  <form action="#" method="POST">
      <input type="text" name="father.name" value="" placeholder="foo"/>
      <input type="number" name="father.age" value="0" placeholder="0"/>
      <input type="text" name="mother.name" value="" placeholder="foo"/>
      <input type="number" name="mother.age" value="0" placeholder="0"/>
  </form>

validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from marshmallow.validate import Length
  from marshmallow import ValidationError


  class MLength(Length):
      message_min = 'Too short! {min}.'
      message_max = 'Too long! {max}.'


  class AuthenticationForm(mf.Form):
      name = mf.String()
      password = mf.String(validate=MLength(5))
      password_confirm = mf.String()

      @mf.Form.validator
      def same(schema, data):
          if data["password"] != data["password_confirm"]:
              raise ValidationError("not same!", "password")


  input_data = {"name": "foo", "password": "*", "password_confirm": "+"}
  form = AuthenticationForm(input_data)
  print(form.validate())  # False
  print(form.errors) # {'password': ['Too short! 5.', 'not same!']}
  {'password': ['Too short! 5.', 'not same!']}

# build your own library
