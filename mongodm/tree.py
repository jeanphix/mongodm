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
    path = StringField()
    order = IntegerField()
    depth = IntegerField()

    @property
    def children(self):
        """ getting node children """
        pass

    def _to_dict(self):
        """ getting object as dict for mongo """
        if self.parent:
            print self.parent._datas
#            self.path = self.parent.path + '/'
        else:
            if self.id:
                self.path = '/'
        return super(TreeDocument, self)._to_dict()