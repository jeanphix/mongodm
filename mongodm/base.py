class ValidationError:
    pass

class DocumentMeta(type):

    def __call__(cls, *args, **kwargs):
        """
        Construct new Document instance, settings _fields
        """
        if cls._fields is None:
            cls._fields = {}
        for name in dir(cls):
            if not name.startswith('_'):
                cls._fields[name] = getattr(cls, name)
        return type.__call__(cls, *args, **kwargs)

    def collection(cls, db):
        db.connection.document_class = cls
        return getattr(db, cls.__collection__)

class BaseDocument(object):

    __metaclass__ = DocumentMeta

    _fields = None

    _id = None


    def __setitem__(self, key, value):
        
        setattr(self, key, value)

    def _to_dict(self):
        dict = {}
        if self._id:
            dict['_id'] = self._id
        print('to_dict')
        for field in self._fields:
            if getattr(self, field):
                dict[field] = self._fields[field]._to_dict()
        return dict

class BaseField(object):

    _value = None

    def __set__(self, instance, value):
        if(self._validate(value)):
            self._value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self._value

    def _validate(self, value):
#        raise ValidationError
        return True

    def _to_dict(self):
        return self._value