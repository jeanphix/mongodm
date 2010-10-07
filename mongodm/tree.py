import re
from pymongo import ASCENDING, DESCENDING
from mongodm.base import BaseDocument
from mongodm.fields import StringField, IntegerField

class TreeDocument(BaseDocument):
    """ Tree document class """
    path = StringField(default='')
    priority = IntegerField(default=0)
    depth = IntegerField(default=0)

    @property
    def children(self):
        """ getting node children """
        path = self.path + str(self.id) + ','
        self._children = self.__class__.collection().find(
            {'path' : re.compile('^' + path)}
        ).sort([('path', ASCENDING), ('priority', DESCENDING)])
        return self._children

    def _to_dict(self):
        """ object to dict for mongo """
        if self.parent:
            self.path = self.parent.path + str(self.parent.id) + ','
        return super(TreeDocument, self)._to_dict()