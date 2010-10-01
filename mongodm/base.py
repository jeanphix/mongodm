from mongodm.collection import CollectionProxy

_document_registry = {}

def get_document_class(name):
    return _document_registry[name]

class ValidationError:
    pass

class DocumentMeta(type):

    def __new__(cls, name, bases, attrs):
        new_class = super(DocumentMeta, cls).__new__(cls, name, bases, attrs)
        _document_registry[name] = new_class
        return new_class

    def collection(cls, db):
        """ getting pymongo collection for document class """
        collection = getattr(db, cls.__collection__)
        collection.__class__ = CollectionProxy
        collection.__itemclass__ = cls
        return collection

class BaseDocument(object):
    
    __metaclass__ = DocumentMeta

    def __init__(self, _id=None,  datas=None):
        """ constructor """
        self._id = _id
        self._fields = {}
        self._datas = {}
        #building private datas and fields
        for name in dir(self.__class__):
            if not name.startswith('_'):
                field = getattr(self.__class__, name)
                field.name = name
                self._fields[name] = field
                if datas and datas[name]:
                    self._fields[name]._from_dict(self, datas[name])
                else:
                    self._datas[name] = self._fields[name].get_default() #default datas

    def __setitem__(self, key, value):
        """ list style data access (required for pymongo)"""
        setattr(self, key, value)

    def __setattr__(self, name, value, validate=False):
        """ setting attribute """
        if not name.startswith('_') and self._fields.has_key(name):
            if validate:
                if self._fields[name].validate(value):
                    self._datas[name] = value
                else:
                    raise ValidationError
            else:
                self._datas[name] = value
        else:
            super(BaseDocument, self).__setattr__(name, value)

    def _to_dict(self):
        """ getting datas as dict """
        if self._id:
            dict = {'_id': self._id}
        else:
            dict={}
        for field in self._fields:
            dict[field] = self._fields[field]._to_dict(self._datas[field])
        return dict

class BaseField(object):

    name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            if instance._datas:
                return instance._datas[self.name]
        
    def validate(self, value):
        """ validate datas """
        return True

    def _to_dict(self, value):
        return value

    def _from_dict(self, object, datas):
        setattr(object, self.name, datas)

    def get_default(self):
        return None