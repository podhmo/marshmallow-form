# -*- coding:utf-8 -*-
import marshmallow_form as mf
from mako.template import Template


class StudentForm(mf.Form):
    name = mf.String(placeholder="foo")
    age = mf.Int(placeholder="0")
    color = mf.Select([(i, c) for i, c in enumerate(["red", "blue", "green", "yellow"])])
    group = mf.Select([("group1", [("a", "a"), ("b", "b")]), ("group2", [("x", "x"), ("y", "y")])], optgroup=True)

template = Template("""
<form>
  <label> ${form.name["label"]}
    <input name="${form.name.name}" value="${form.name.value}" placeholder="${form.name['placeholder']}"/>
  </label>
  <label> ${form.name["label"]}
    <input name="${form.age.name}" value="${form.age.value}" placeholder="${form.age['placeholder']}"/>
  </label>
  <select name="${form.color.name}">
    %for c in form.color.choices:
    <option name="${form.color.name}" value="${c[0]}">${c[1]}</option>
    %endfor
  </select>
  <select name="${form.group.name}">
    %for g in form.group.choices:
    <optgroup label="${g[0]}">
      %for c in g[1]:
        <option name="${form.group.name}" value="${c[0]}">${c[1]}</option>
      %endfor
    </optgroup>
    %endfor
  </select>
</form>
""")

import threading
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults


def app(environ, start_response):
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf8')]

    start_response(status, headers)

    form = StudentForm()
    return [template.render(form=form).encode("utf-8")]

server = make_server("", 8000, app)
t = threading.Thread(target=server.handle_request, daemon=True)
try:
    t.start()
    import webbrowser
    webbrowser.open("http://localhost:8000")
except Exception as e:
    print(e)
finally:
    t.join()
