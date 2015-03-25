# -*- coding:utf-8 -*-
from jinja2 import Template
from functools import partial
import marshmallow_form as mf
from marshmallow_form.layout import Layout, LColumn


Int = partial(mf.Int, type="number")
Str = partial(mf.Str, type="text")


class DateTriple(mf.Form):
    year = Int()
    month = Int()
    day = Int()


class FileForm(mf.Form):
    name = Str()
    ctime = mf.Nested(DateTriple)


template = Template("""
<form action="#" method="POST">
{% for f in form %}\
  <input name="{{f.name}}" value="{{f.value}}" type="{{f.type}}"
{% endfor %}\
</form>
""")


form = FileForm()
print(template.render(form=form))
# <form action="#" method="POST">
#   <input name="name" value="" type="text"
#   <input name="ctime.year" value="0" type="number"
#   <input name="ctime.month" value="0" type="number"
#   <input name="ctime.day" value="0" type="number"
# </form>


class FileForm2(mf.Form):
    name = Str()
    ctime = mf.Nested(DateTriple)

    class Meta:
        layout = Layout([
            LColumn("name", widget="row"),
            LColumn("ctime.year", "ctime.month", "ctime.day", widget="tri")
        ])


template = Template("""
<form action="#" method="POST">
{% for lcol, fields in form %}
  {% if lcol.widget == "tri" %}
  <div class="tri">
    {% for f in fields %}
     <input name="{{f.name}}" value="{{f.value}}" type="{{f.type}}"
    {% endfor %}
  </div>
  {% else %}
  <div class="row">
    {% for f in fields %}
     <input name="{{f.name}}" value="{{f.value}}" type="{{f.type}}"
    {% endfor %}
  </div>
  {% endif %}
{% endfor %}
</form>
""")

form = FileForm2()
print(template.render(form=form))
"""
<form action="#" method="POST">

  
  <div class="row">
    
     <input name="name" value="" type="text"
    
  </div>
  

  
  <div class="tri">
    
     <input name="ctime.year" value="0" type="number"
    
     <input name="ctime.month" value="0" type="number"
    
     <input name="ctime.day" value="0" type="number"
    
  </div>
  

</form>
"""
