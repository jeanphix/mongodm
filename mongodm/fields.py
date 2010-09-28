from mongodm.base import BaseField

class ListField(BaseField):
    def __init__(self, allowed):
        self.allowed = allowed

    def _to_dict(self, value):
        """ getting collection as dict """
        dict = []
        for item in value:
            dict.append(item._to_dict())
        return dict

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