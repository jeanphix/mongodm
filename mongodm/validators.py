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
        
    def __call__(self, value):
        if not self.regex.match(value or u''):
            raise ValidationError(self.message)
            
class Email(Regex):
    """
    Email validator
    """
    def __init__(self, message=_(u'Invalid email address.')):
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE, message)
