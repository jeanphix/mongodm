import pymongo

class CollectionProxy(pymongo.collection.Collection):
    """ collection proxy """
    def insert(self, document, *args, **kwargs):
        """ proxying insert """
        super(CollectionProxy, self).insert(document._to_dict(), *args, **kwargs)

    def find(self, *args, **kwargs):
        if self.__itemclass__ :
            return super(CollectionProxy, self).find(
                as_class=self.__itemclass__, *args, **kwargs)
        else:
            return super(CollectionProxy, self).find(*args, **kwargs)
