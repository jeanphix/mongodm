from wtforms import Form, HiddenField
from mongodm.base import BaseField

class MongodmForm(Form):

    __forclass__ = None

    id = HiddenField()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """ constructor override """
        self._obj = obj
        super(MongodmForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)


    def validate(self):
        """ overriding validation """
        success = super(MongodmForm, self).validate()
        for name in dir(self.__forclass__):
            if not name.startswith('_')\
                   and not name == 'id'\
                   and issubclass(getattr(self.__forclass__, name).__class__, BaseField):
                if hasattr(self, name):
                    field = getattr(self.__forclass__, name)
                    try:
                        if self._obj:
                            field.validate(getattr(getattr(self, name), 'data'), obj=self._obj)
                        else:
                            field.validate(getattr(getattr(self, name), 'data'), class_=self.__forclass__)
                    except ValueError, e:
                        success = False
                        getattr(self, name).errors.append(e.args[0])                        
        return success

