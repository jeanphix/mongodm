from mongodm.base import BaseDocument
from mongodm.fields import StringField, IntegerField, ReferenceField

class TreeProxy():
    """ tree proxy class for trees management """
    def __init__(self, node_class):
        self._node_class = node_class

    def from_dict(self):
        """ return tree from dict or SON """
        pass

    def find_tree_from_path(self, path):
        """ finding tree from path """
        pass

class TreeDocument(BaseDocument):
    """ Tree document class """
    path = StringField(default='/')
    order = IntegerField(default=0)
    depth = IntegerField()

    @property
    def children(self):
        """ getting node children """
        pass

    def _to_dict(self):
        """ getting object as dict for mongo """
        if self.parent:
            self.path = self.parent.path + str(self.parent.id) + '/'
        return super(TreeDocument, self)._to_dict()