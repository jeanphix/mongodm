from mongodm.base import BaseField, get_document_class

class ListField(BaseField):
    def __init__(self, allowed):
        self._allowed = allowed

    def _to_dict(self, value):
        """ getting collection as dict """
        dict = []
        for item in value:
            dict.append(item._to_dict())
        return dict

    def _from_dict(self, object, datas):
        list = []
        for document in datas:
            list.append(get_document_class(self._allowed)(datas=document._datas))
        setattr(object, self.name, list)

    def get_default(self):
        return []
      
class StringField(BaseField):
    pass

class EmbeddedDocumentField(BaseField):

    def __init__(self, allowed):
        self._allowed = allowed

    def _to_dict(self, value):
        if value:
            return value._to_dict()

    def _from_dict(self, object, datas):
        embedded = get_document_class(self._allowed)(datas=datas._datas)
        setattr(object, self.name, embedded)
