import pymongo
from bson import SON

class MongoDocument(SON):
    """ simple dot access class for pymongo backed document """
    def __setitem__(self, key, value):
        if key == '_id':
            self._id = value
        else:
            super(MongoDocument, self).__setitem__(key, value)
            
    def to(self, new_class):
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
        document._id = super(CollectionProxy, self).insert(document._to_dict(),
                                                            *args, **kwargs)
        return document._id

#    def update(self, document, *args, **kwargs):
#        """ proxying save """
#        document._id = super(CollectionProxy, self).update(document._to_dict(),
#                                                            *args, **kwargs)
#        return document._id

    def save(self, document, *args, **kwargs):
        """ proxying save """
        document._id = super(CollectionProxy, self).save(document._to_dict(),
                                                            *args, **kwargs)
        return document._id

    def find(self, *args, **kwargs):
        """ proxying find """
        if self.__itemclass__ :
            return super(CollectionProxy, self).find(
                as_class=MongoDocument, *args, **kwargs)
        else:
            return super(CollectionProxy, self).find(*args, **kwargs)