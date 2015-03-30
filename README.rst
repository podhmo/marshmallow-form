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

features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- having metadata anywhere
- nested field support
- accessing schema
- building your own form library


getting started
----------------------------------------

install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from pypi package repository.

::

   # pip install marshmallow-form

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


detail
----------------------------------------

having metadata anywhere
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- form metadata
- field metadata
- metadata inheritance
- metadata override

form metadata

.. code-block:: python

  import marshmallow_form as mf


  class MyForm(mf.Form):
      name = mf.Str()

      class Meta:
          metadata = {"action": "#"}

  form = MyForm()
  form["action"]  # => #
  form.metadata["method"] = "post"
  form["method"]  # => "post"

  MyForm()["method"]  # => ""


field metadata

.. code-block:: python

  class MyForm2(mf.Form):
      name = mf.Str()
      ctime = mf.DateTime(disable=True)


  form = MyForm2()
  form.ctime["disable"]  # => True

metadata inheritance

.. code-block:: python

  from functools import partial
  DateTime = partial(mf.DateTime, widget="tdcalendar")


  class MyForm3(mf.Form):
      ctime = DateTime()
      utime = DateTime()

  form = MyForm3()
  form.ctime["widget"]  # => "tdcalendar"
  form.utime["widget"]  # => "tdcalendar"

metadata override

.. code-block:: python

  class MyForm4(MyForm3):
      class Meta:
          overrides = {"ctime": {"widget": "mycalendar"}}


  form = MyForm4()
  form.ctime["widget"]  # => "mycalendar"
  form.utime["widget"]  # => "tdcalendar"

or with nested

.. code-block:: python

  class PersonForm(mf.Form):
      name = mf.String(label="名前", placeholder="foo", widget="str")
      age = mf.Integer(label="年齢", placeholder="0", widget="int")


  class ParentsForm(mf.Form):
      father = mf.Nested(PersonForm, label="父親", overrides={"name": {"label": "父親の名前"}})
      mother = mf.Nested(PersonForm, label="母親")

  form = ParentsForm()
  form.father["label"]  # => "父親"
  form.father.name["label"]  # => "父親の名前"
  form.mother.name["label"]  # => "名前"


dynamic form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- modify field
- add field
- remove field

modify field

.. code-block:: python

  form = StudentForm()
  form.color.metadata["pairs"] = [("red", "red"), ("blue", "blue")]
  form.color["pairs"]  # => [('red', 'red'), ('blue', 'blue')]


add field

.. code-block:: python

  class StudentForm(mf.Form):
      color = mf.Select([])
      name = mf.Str()

  form = StudentForm(initial={"grade": 3})
  form.add_field("grade", mf.Int(label="学年"))
  form.grade.value  # => 3
  form.grade["label"]  # => "学年"

  [f.name for f in form]  # => ['color', 'name', 'grade']

remove field

.. code-block:: python

  form = StudentForm()
  form.remove_field("color")

  [f.name for f in form]  # => ['name']



accessing schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- schema class
- schema instance

schema class

.. code-block:: python

  from collections import namedtuple
  Person = namedtuple("Person", "name age")


  class PersonForm(mf.Form):
      name = mf.Str()
      age = mf.Int()

      def make_object(self, data):
          return Person(**data)

  PersonForm.Schema  # => <class 'marshmallow.schema.PersonSchema'>

  schema = PersonForm.Schema(many=True)
  schema.dump([Person("foo", 20), Person("bar", 20)]).data
  # => OrderedDict([('name', 'foo'), ('age', 20)]), OrderedDict([('name', 'bar'), ('age', 20)])

schema instance

.. code-block:: python

  form = PersonForm()
  form.schema.load({"name": "foo", "age": 20}).data  # => Person(name='foo', age=20)


building your own form library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- define your form field class
- define the way of rendering

define your form field class

if just only adding default metadata, using functools.partial.

.. code-block:: python

  import functools
  PositiveInt = functools.partial(mf.Int, validate=lambda x: x > 0)

  class Form(mf.Form):
      x = PositiveInt()

  print(Form({"x": "-10"}).load())
  # UnmarshalResult(data=OrderedDict([('x', None)]), errors={'x': ['Validator <lambda>(-10) is False']})

if define your own field class

.. code-block:: python

  from marshmallow.fields import Field
  from marshmallow.exceptions import UnmarshallingError
  import base64


  class Base64(Field):
      """ tiny base64 field"""
      def __init__(self, *args, **kwargs):
          super(Base64, self).__init__(*args, **kwargs)

      def _serialize(self, value, attr, obj):
          return base64.encodebytes(value)

      def _deserialize(self, value):
          try:
              return base64.decodebytes(value.encode("utf-8"))
          except:
              raise UnmarshallingError("oops")

  MyBase64 = mf.field_factory(Base64)


  class Form(mf.Form):
      x = MyBase64(label="this is broken")

  form = Form({"x": "MTEx"})
  print(form.load())
  # UnmarshalResult(data=OrderedDict([('x', b'111')]), errors={})

define the way of rendering

.. code-block:: python

  def input(field, placeholder=""):
      fmt = '<input name="{name}" value="{value}" placeholder="{placeholder}">'
      return fmt.format(name=field["name"], value=field.value, placeholder=placeholder)


  class Form(mf.Form):
      name = mf.Str(__call__=input)

  form = Form()
  print(form.name(placeholder="foo"))
  # => <input name="" value="" placeholder="foo">

