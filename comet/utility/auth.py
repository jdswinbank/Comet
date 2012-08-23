from functools import wraps

from ..icomet import IAuthenticatable
from ..log import log
from signature import sigchecker

class CheckSignatureMixin(object):
    def authenticate(self, packet):
        def do_authenticate(is_valid):
            # If the subscriber is not successfully authenticated, sigchecker
            # will errback and this code will never run. In other words, if we
            # get here, the subscriber is good.
            log.msg("Authenticating subscriber")
            self.authenticated = True

        return sigchecker(packet).addCallback(do_authenticate)

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
