import pymongo

class MongoDocument(object):
    """ simple dot access class for pymongo backed document """
    def __init__(self):
        self._datas = {}
        self._id = None

    def __setitem__(self, key, value):
        if key == '_id':
            self._id = value
        else:
            self._datas[key] = value

    def __getattr__(self, key):
        return self._datas[key]

    def to(self, new_class):
        object = new_class(_id=self._id, datas = self._datas)
        return object

class CollectionProxy(pymongo.collection.Collection):
    """ collection proxy """
    def insert(self, document, *args, **kwargs):
        """ proxying insert """
        document._id = super(CollectionProxy, self).insert(document._to_dict(),
                                                            *args, **kwargs)
        return document._id

    def find(self, *args, **kwargs):
        """ proxying find """
        if self.__itemclass__ :
            return super(CollectionProxy, self).find(
                as_class=MongoDocument, *args, **kwargs)
        else:
            return super(CollectionProxy, self).find(*args, **kwargs)