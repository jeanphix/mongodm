from mongodm.collection import CollectionProxy
from pymongo.objectid import ObjectId

_document_registry = {}

def get_document_class(name):
    return _document_registry[name]


class DocumentMeta(type):

    def __new__(cls, name, bases, attrs):
        """ registering document classes """
        new_class = super(DocumentMeta, cls).__new__(cls, name, bases, attrs)
        _document_registry[name] = new_class
        return new_class

    def collection(cls):
        """ getting pymongo collection for document class """
        collection = getattr(cls.__db__, cls.__collection__)
        collection.__class__ = CollectionProxy
        collection.__itemclass__ = cls
        return collection

class BaseField(object):

    name = None #bounded name

    def __init__(self, validators=[], default=None):
        """ constructor """
        self._validators=validators
        self._default = default

    def __get__(self, instance, owner):
        """ foreign getter """
        if instance is None:
            return self
        elif instance._datas:
                return instance._datas[self.name]

    def validate(self, value, obj=None, class_=None):
        """ validate datas """
        for validator in self._validators:
            validator(value, field=self, obj=obj, class_=class_)

    def to_dict(self, value):
        return value

    def from_dict(self, object, datas):
        setattr(object, self.name, datas)

    def get_default(self):
        return self._default
      
class BaseDocument(object):

    __metaclass__ = DocumentMeta

    def __init__(self, _id=None, datas=None):
        """ constructor """
        self._id = _id #@todo : move _id into self._datas
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
                    self._fields[name].from_dict(self, datas[name])
                else:
                    self._datas[name] = self._fields[name].get_default() #default datas

    def __setitem__(self, key, value):
        """ list style data access (required for pymongo)"""
        setattr(self, key, value)

    def __setattr__(self, name, value):
        """ setting attribute """
        if not name.startswith('_') and self._fields.has_key(name):
            self._datas[name] = value
        else:
            super(BaseDocument, self).__setattr__(name, value)

    def to_dict(self):
        """ getting datas as dict """
        self.validate()
        if self._id:
            dict = {'_id': ObjectId(self._id)}
        else:
            dict={}
        for field in self._fields:
            dict[field] = self._fields[field].to_dict(self._datas[field])
        return dict

    def validate(self):
        """ validate data """
        for field in self._fields:
            self._fields[field].validate(self._datas[field], obj=self)
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value