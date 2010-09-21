import pymongo

class CollectionProxy(pymongo.collection.Collection):
    """ collection proxy """
    def insert(self, document, manipulate=True, safe=False, check_keys=True):
        """ proxying insert """
        super(CollectionProxy, self).insert(
            document._to_dict(),
            manipulate,
            safe,
            check_keys
        )