from mongodm.base import BaseField

class StringField(BaseField):
    pass

class ListField(BaseField):

    

    def __init__(self, allowed):
        print(allowed)