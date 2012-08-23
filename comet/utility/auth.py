from functools import wraps

from ..icomet import IAuthenticatable
from ..log import log

class CheckSignatureMixin(object):
    def authenticate(self, packet):
        # Todo
        self.authenticated = True

def check_auth(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if IAuthenticatable.providedBy(self):
            if not self.must_auth or (self.must_auth and self.authenticated):
                return f(self, *args, **kwargs)
            else:
                log.warning("Denying authentication")
        else:
            log.warning(
                "Authentication denied for non authenticatable %s!" % (str(self))
            )
    return wrapper
