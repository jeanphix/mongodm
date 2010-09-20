import unittest
import pymongo
import mongodm

from mongodm.base import BaseDocument
from mongodm.document import Document
from mongodm.fields import StringField, ListField
from pymongo import Connection

class Post(Document):
    __collection__ = 'posts'
    title = StringField()
    content = StringField()
    comments = ListField('Comment')

class Comment(Document):
    author = StringField
    message = StringField

class Reply(Document):
    author = StringField
    message = StringField

#connection = Connection('localhost', 27017)
connection = Connection('localhost', 27017)
connection.document_class=Document
db = connection['test-database']


class DocumentTest(unittest.TestCase):

    def test_init_document(self):
          post = Post()
          assert len(post._fields)==3
          issubclass(post.__class__, Document)
          post.title = 'first post title'
          post.content = 'first post content'
          assert post.title == 'first post title'
          assert post._to_dict()=={
              'content': 'first post content',
              'title': 'first post title'
          }
          post.title = 'first post title modified'
          assert post._to_dict()=={
              'content': 'first post content',
              'title': 'first post title modified'
          }

          Post.collection(db).insert(post._to_dict())

          post = Post.collection(db).find_one()

          assert post.title == u'first post title modified'
          print(post._to_dict())

          print(post._id)
#          db.posts.remove()

if __name__ == '__main__':
    unittest.main()