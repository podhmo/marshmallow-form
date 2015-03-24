# -*- coding:utf-8 -*-
from mako.template import Template
import marshmallow_form as mf
from datetime import date
from collections import namedtuple
Person = namedtuple("Person", "name birth")


class PersonForm(mf.Form):
    name = mf.String()
    birth = mf.Date()

    @mf.Form.accessor
    def access(self, k, ob):
        return getattr(ob, k)

people = [
    Person(name="foo", birth=date(2000, 1, 1)),
    Person(name="bar", birth=date(2000, 1, 2)),
    Person(name="boo", birth=date(2000, 1, 3))
]

template = Template("""
%for person in people:
<dl>
  %for f in person:
  <dt>${f.name}</dt>
  <dd>${f.value}</dd>
  %endfor
</dl>
%endfor
""")

print(template.render(people=map(PersonForm.from_object, people)))
"""
# output
<dl>
  <dt>name</dt>
  <dd>foo</dd>
  <dt>birth</dt>
  <dd>2000-01-01</dd>
</dl>
<dl>
  <dt>name</dt>
  <dd>bar</dd>
  <dt>birth</dt>
  <dd>2000-01-02</dd>
</dl>
<dl>
  <dt>name</dt>
  <dd>boo</dd>
  <dt>birth</dt>
  <dd>2000-01-03</dd>
</dl>
"""
