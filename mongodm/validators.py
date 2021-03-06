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
        
    def __call__(self, value, field=None, obj=None, class_=None):
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

    def __call__(self, value, field=None, obj=None, class_=None):
        if not value or isinstance(value, basestring) and not value.strip():
            raise ValidationError(self.message)

class Unique(object):
    """
    Unique validator
    """
    def __init__(self, message=_(u'Already exists in database.')):
        self.message = message

    def __call__(self, value, field=None, obj=None, class_=None):
        if obj:
            backed = obj.__class__.collection().\
                                            find_one({field.name: value})
        else:
            if class_:
                backed = class_.collection().\
                                            find_one({field.name: value})
        if backed != None and not obj or obj and backed != None and str(backed._id) != str(obj._id):
            raise ValidationError(self.message)

class Integer(object):
    """
    Integer validator
    """
    def __init__(self, message=_(u'Invalid integer.')):
        self.message = message

    def __call__(self, value, field=None, obj=None, class_=None):
        if value and value != '':
            try:
                int(value)
                if int(value) != value:
                    raise ValidationError(self.message)
            except:
                raise ValidationError(self.message)

class Decimal(object):
    """
    Decimal validator
    """
    def __init__(self, message=_(u'Invalid integer.')):
        self.message = message

    def __call__(self, value, field=None, obj=None, class_=None):
        if value and value != '':
            try:
                float(value)
            except:
                raise ValidationError(self.message)
