from wtforms import Form, HiddenField

class MongodmForm(Form):

    __forclass__ = None

    id = HiddenField()

    def validate(self):
        """ overriding validation """
        success = super(MongodmForm, self).validate()
        for name in dir(self.__forclass__):
            if not name.startswith('_') and not name == 'id':
                if hasattr(self, name):
                    field = getattr(self.__forclass__, name)
                    try:
                        field.validate(getattr(getattr(self, name), 'data'), class_=self.__forclass__)
                    except ValueError, e:
                        success = False
                        getattr(self, name).errors.append(e.args[0])                        
        return success