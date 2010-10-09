from mongodm.connection import Connection
from mongodm.fields import StringField, ListField, ReferenceField
from mongodm.document import Document

connection = Connection('localhost', 27017)
db = connection['test-database']

class TreeNode(Document):
    __collection__ = 'nodes'
    __db__ = db
    label = StringField()
    children = ListField(ReferenceField('TreeNode'))

root = TreeNode()
root.label = 'root'
TreeNode.collection().insert(root)


first_child = TreeNode()
first_child.label = 'node 1'
root

second_child = TreeNode()
second_child.label = 'node 1.1'
first_child.children.append(second_child)

third_child = TreeNode()
third_child.label = 'node 1.2'
first_child.children.append(third_child)

