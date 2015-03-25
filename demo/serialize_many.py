# -*- coding:utf-8 -*-
from marshmallow import Schema, fields
from collections import namedtuple
from datetime import datetime
from mako.template import Template


class CommentSchema(Schema):
    id = fields.Int()
    text = fields.String()
    created_at = fields.DateTime()
    parent_id = fields.Int()

    class Meta:
        fields = ('id', 'text', 'created_at', 'parent_id')


class LikeSchema(Schema):
    id = fields.Int()
    created_at = fields.DateTime()
    parent_id = fields.Int()

    class Meta:
        fields = ('id', 'created_at', 'parent_id')


class ParentSchema(Schema):
    comments = fields.Nested(CommentSchema, many=True)
    likes = fields.Nested(LikeSchema, many=True)
    description = fields.Str()
    title = fields.Str()

    class Meta:
        fields = ('id', 'title', 'description', 'comments', 'likes')


Parent = namedtuple("Parent", "id title description comments likes")
Like = namedtuple("Like", "id created_at parent_id")
Comment = namedtuple("Comment", "id text created_at parent_id")

now = datetime.now()

parent = Parent(
    id=1,
    title="this is title of article",
    description="long long text",
    comments=[
        Comment(id=1, text="hmm", created_at=now, parent_id=1),
        Comment(id=2, text="...", created_at=now, parent_id=1)
    ],
    likes=[
        Like(id=1, created_at=now, parent_id=1),
        Like(id=2, created_at=now, parent_id=1),
        Like(id=3, created_at=now, parent_id=1),
    ],
)

schema = ParentSchema()

# pprint(schema.dump(parent).data, indent=2)
# { 'comments': [ { 'created_at': '2015-03-25T18:32:40.901066+00:00',
#                   'id': 1,
#                   'parent_id': 1,
#                   'text': 'hmm'},
#                 { 'created_at': '2015-03-25T18:32:40.901066+00:00',
#                   'id': 2,
#                   'parent_id': 1,
#                   'text': '...'}],
#   'description': 'long long text',
#   'id': 1,
#   'likes': [ { 'created_at': '2015-03-25T18:32:40.901066+00:00',
#                'id': 1,
#                'parent_id': 1},
#              { 'created_at': '2015-03-25T18:32:40.901066+00:00',
#                'id': 2,
#                'parent_id': 1},
#              { 'created_at': '2015-03-25T18:32:40.901066+00:00',
#                'id': 3,
#                'parent_id': 1}],
#   'title': 'this is title of article'}

import marshmallow_form as mf


class ParentForm(mf.form_factory("_ParentForm", ParentSchema)):
    class Meta:
        overrides = {
            "description": {"ja": "概要"},
            "comments": {"ja": "コメント"}
        }


template = Template("""
${form.description['ja']}: ${form.description.value}
${form.comments['ja']}:
%for c in form.comments:
 - ${c.id.value}(${c.created_at.value})
%endfor
${form.likes['ja'] or form.likes._name}:
%for c in form.likes:
 - ${c.id.value}(${c.created_at.value})
%endfor
""")


form = ParentForm.from_object(parent)
print(template.render(form=form))

# 概要: long long text
# コメント:
#  - 1(2015-03-25T22:20:56.635734+00:00)
#  - 2(2015-03-25T22:20:56.635734+00:00)
# likes:
#  - 1(2015-03-25T22:20:56.635734+00:00)
#  - 2(2015-03-25T22:20:56.635734+00:00)
#  - 3(2015-03-25T22:20:56.635734+00:00)
