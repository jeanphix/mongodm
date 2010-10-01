from mongodm.base import BaseField, get_document_class

class ListField(BaseField):
    def __init__(self, allowed):
        """ construct """
        self._allowed = allowed

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

    def __init__(self, allowed):
        """ construct """
        self._allowed = allowed

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