from mongodm.base import BaseField, get_document_class

class ListField(BaseField):
    def __init__(self, allowed):
        self.allowed = allowed

    def _to_dict(self, value):
        """ getting collection as dict """
        dict = []
        for item in value:
            dict.append(item._to_dict())
        return dict

    def _from_dict(self, object, datas):
        setattr(object, self.name, datas)

    def get_default(self):
        return []
      
class StringField(BaseField):
    pass

class EmbeddedDocumentField(BaseField):

    def __init__(self, allowed):
        self._allowed_class = get_document_class(allowed)

    def _to_dict(self, value):
        if value:
            return value._to_dict()

    def _from_dict(self, object, datas):
        embedded = self._allowed_class(datas=datas._datas)
        setattr(object, self.name, embedded)
