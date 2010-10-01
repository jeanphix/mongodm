from wtforms import Form
from wtforms.form import FormMeta

class MongodmForm(Form):

    __forclass__ = None

    def validate(self):
        """ overriding validation """
        success = super(MongodmForm, self).validate()
        for name in dir(self.__forclass__):
            if not name.startswith('_'):
                field = getattr(self.__forclass__, name)
                if hasattr(self, name):
                    try:
                        field.validate(getattr(getattr(self, name), 'data'))
                    except ValueError, e:
                        getattr(self, name).errors.append(e.args[0])                        
        return
  
    
