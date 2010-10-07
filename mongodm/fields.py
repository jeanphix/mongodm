from mongodm.base import BaseField, get_document_class
from mongodm.validators import Email, Decimal, Integer
from pymongo.dbref import DBRef
from bson.son import SON

class ListField(BaseField):
    def __init__(self, allowed, *args, **kwargs):
        """ construct """
        self._allowed = allowed
        super(ListField, self).__init__(*args, **kwargs)
        
    def _to_dict(self, value):
        """ getting collection as dict """
        dict = []
        for item in value:
            dict.append(item._to_dict())
        return dict

    def _from_dict(self, object, datas):
        """ hydrating collection from dict """
        list = []
        if isinstance(self._allowed, str):
            self._allowed = get_document_class(self._allowed)
        for document in datas:
            list.append(self._allowed(datas=document._datas))
        setattr(object, self.name, list)

    def get_default(self):
        """ defining default value """
        return []
      
class EmbeddedDocumentField(BaseField):
    def __init__(self, allowed, *args, **kwargs):
        """ construct """
        self._allowed = allowed
        super(EmbeddedDocumentField, self).__init__(*args, **kwargs)

    def _to_dict(self, value):
        """ getting embedded document as dict """
        if value:
            return value._to_dict()

    def _from_dict(self, object, datas):
        """ hydrating embedded document from dict """
        if isinstance(self._allowed, str):
            self._allowed = get_document_class(self._allowed)
        embedded = self._allowed(datas=datas._datas)
        setattr(object, self.name, embedded)

class StringField(BaseField):
    pass

class EmailField(BaseField):
    def __init__(self, validators=[], *args, **kwargs):
        """ constructor """
        validators.extend([Email()])
        super(EmailField, self).__init__(validators=validators, *args, **kwargs)

class EnumField(BaseField):
    def __init__(self, enum, *args, **kwargs):
        """ construct """
        self._enum = enum
        super(EnumField, self).__init__(*args, **kwargs)

class IntegerField(BaseField):
    def __init__(self, validators=[], *args, **kwargs):
        """ constructor """
        validators.extend([Integer()])
        super(IntegerField, self).__init__(validators=validators, *args, **kwargs)
    
    def get_default(self):
        if self._default:
            return self._default
        else:
            return 0

class DecimalField(BaseField):
    def __init__(self, validators=[], *args, **kwargs):
        """ constructor """
        validators.extend([Decimal()])
        super(DecimalField, self).__init__(validators=validators, *args, **kwargs)

    def get_default(self):
        if self._default:
            return self._default
        else:
            return 0

class ReferenceField(BaseField):
    """ DBRef field """
    def __init__(self, allowed, *args, **kwargs):
        """ construct """
        self._allowed = allowed
        super(ReferenceField, self).__init__(*args, **kwargs)
    
    def _to_dict(self, value):
        """ getting DBRef """
        if value:
            return DBRef(value.__class__.__collection__, value._id)

    def __get__(self, instance, owner):
        """ foreign getter """
        if isinstance(self._allowed, str):
            self._allowed = get_document_class(self._allowed)
        db = self._allowed.__db__
        if instance is None:
            return self
        else:
            if instance._datas and instance._datas[self.name].__class__ == self._allowed:
                return instance._datas[self.name]
            elif instance._datas[self.name] != None:
                return self._allowed(_id=instance._datas[self.name].id, datas=db.dereference(instance._datas[self.name]))
