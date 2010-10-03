from mongodm.collection import CollectionProxy
from mongodm.validators import ValidationError

_document_registry = {}

def get_document_class(name):
    return _document_registry[name]


class DocumentMeta(type):

    def __new__(cls, name, bases, attrs):
        """ registering document classes """
        new_class = super(DocumentMeta, cls).__new__(cls, name, bases, attrs)
        _document_registry[name] = new_class
        return new_class

    def collection(cls, db):
        """ getting pymongo collection for document class """
        collection = getattr(db, cls.__collection__)
        collection.__class__ = CollectionProxy
        collection.__itemclass__ = cls
        return collection

class BaseField(object):

    name = None #bounded name

    def __init__(self, validators=[]):
        """ constructor """
        self._validators=validators

    def __get__(self, instance, owner):
        """ foreign getter """
        if instance is None:
            return self
        else:
            if instance._datas:
                return instance._datas[self.name]

    def validate(self, value, object = None, class_=None):
        """ validate datas """
        for validator in self._validators:
            validator(value, field=self, object=object, class_=class_)
        return True

    def _to_dict(self, value):
        return value

    def _from_dict(self, object, datas):
        setattr(object, self.name, datas)

    def get_default(self):
        return None
      
class BaseDocument(object):

    __metaclass__ = DocumentMeta

    def __init__(self, _id=None, datas=None):
        """ constructor """
        self._id = _id
        self._fields = {}
        self._datas = {}
        #building private datas and fields
        for name in dir(self.__class__):
            if not name.startswith('_') and not name == 'id'\
                and issubclass(getattr(self.__class__, name).__class__, BaseField):
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

    def __setattr__(self, name, value):
        """ setting attribute """
        if not name.startswith('_') and self._fields.has_key(name):
            if self._fields[name].validate(value, object=self):
                self._datas[name] = value
            else:
                raise ValidationError
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

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
