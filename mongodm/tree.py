from mongodm.base import BaseDocument
from mongodm.fields import StringField, IntegerField
import re

class TreeDocument(BaseDocument):
    """ Tree document class """
    path = StringField(default='')
    order = IntegerField(default=0)
    depth = IntegerField()

    @property
    def children(self):
        """ getting node children """
        path = self.path + str(self.id) + ','
        self._children = self.__class__.collection().find({'path' : re.compile('^' + path)})
        return self._children

    def _to_dict(self):
        """ object to dict for mongo """
        if self.parent:
            self.path = self.parent.path + str(self.parent.id) + ','
        return super(TreeDocument, self)._to_dict()