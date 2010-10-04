import re
from gettext import gettext as _

class ValidationError(ValueError):
    """
    Raised when a validator fails to validate its input.
    """
    def __init__(self, message=u'', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)

class Regex(object):
    """
    Regex validator
    """
    def __init__(self, regex, flags=0, message=_(u'Invalid input.')):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message
        
    def __call__(self, value, field=None, object=None, class_=None):
        if value and not self.regex.match(value or u''):
            raise ValidationError(self.message)
            
class Email(Regex):
    """
    Email validator
    """
    def __init__(self, message=_(u'Invalid email address.')):
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE, message)

class Required(object):
    """
    Required validator
    """
    def __init__(self, message=_(u'This field is required.')):
        self.message = message

    def __call__(self, value, field=None, object=None, class_=None):
        if not value or isinstance(value, basestring) and not value.strip():
            raise ValidationError(self.message)

class Unique(object):
    """
    Unique validator
    """
    def __init__(self, db, message=_(u'Already exists in database.')):
        self.message = message
        self.db = db

    def __call__(self, value, field=None, object=None, class_=None):
        if object:
            backed = object.__class__.collection(self.db).\
                                            find_one({field.name: value})
        else:
            if class_:
                backed = class_.collection(self.db).\
                                            find_one({field.name: value})
        if backed != None and not object or object and backed != None and backed._id != object.id:
            raise ValidationError(self.message)

class Integer(object):
    """
    Integer validator
    """
    def __init__(self, message=_(u'Invalid integer.')):
        self.message = message

    def __call__(self, value, field=None, object=None, class_=None):
        if value and value != '':
            try:
                int(value)
            except:
                raise ValidationError(self.message)

class Decimal(object):
    """
    Decimal validator
    """
    def __init__(self, message=_(u'Invalid integer.')):
        self.message = message

    def __call__(self, value, field=None, object=None, class_=None):
        if value and value != '':
            try:
                float(value)
            except:
                raise ValidationError(self.message)
