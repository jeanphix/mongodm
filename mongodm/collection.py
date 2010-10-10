import pymongo
from bson import SON
#from mongodm.base import get_document_class

class MongoDocument(SON):
    """ simple dot access class for pymongo backed document """
    def __setitem__(self, key, value):
        if key == '_id':
            self._id = value
        else:
            super(MongoDocument, self).__setitem__(key, value)
            
    def to(self, new_class):
#        if isinstance(new_class, str):
#            new_class = get_document_class(new_class)
        object = new_class(_id=self._id, datas = self._datas)
        return object

    def __getattr__(self, key):
        return super(MongoDocument, self).__getitem__(key)

    @property
    def _datas(self):
        return dict(self)

class CollectionProxy(pymongo.collection.Collection):
    """ collection proxy """
    def insert(self, document, *args, **kwargs):
        """ proxying insert """
        document._id = super(CollectionProxy, self).insert(document.to_dict(),
                                                            *args, **kwargs)
        return document._id

    def save(self, document, *args, **kwargs):
        """ proxying save """
        document._id = super(CollectionProxy, self).save(document.to_dict(),
                                                            *args, **kwargs)
        return document._id

    def find(self, *args, **kwargs):
        """ proxying find """
        if self.__itemclass__ :
            return super(CollectionProxy, self).find(
                as_class=MongoDocument, *args, **kwargs)
        else:
            return super(CollectionProxy, self).find(*args, **kwargs)