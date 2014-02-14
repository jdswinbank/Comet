# Comet VOEvent Broker.
# Authentication routines.
# John Swinbank, <swinbank@transientskp.org>.

from functools import wraps
from twisted.internet.threads import deferToThread

from ..icomet import IAuthenticatable
from ..utility import log

def check_for_bad_key(key):
    """
    Returns False if key is suitable for use in signing. Otherwise, returns
    the reason why it isn't.
    """
    if key.expired:
        return "Expired"
    elif key.disabled:
        return "Disabled"
    elif key.invalid:
        return "Invalid"
    elif key.revoked:
        return "Revoked"
    elif not key.can_sign:
        return "Not capable of signing"
    else:
        return False

def check_sig(packet):
    """
    Check the OpenPGP signature on packet.

    Returns a Deferred that provides either a True (signature valid) or False
    (invalid) when it fires.
    """
    def check_validity(is_valid):
        if is_valid:
            log.debug("Packet has good signature")
            return True
        else:
            log.debug("Signature could not be verified")
            return False

    def signature_failure(failure):
        log.warning("Unable to check signature")
        log.err(failure)
        return failure

    return deferToThread(
        packet.valid_signature
    ).addCallbacks(check_validity, signature_failure)

class CheckSignatureMixin(object):
    def authenticate(self, packet):
        def do_authenticate(is_valid):
            # If the subscriber is not successfully authenticated, check_sig
            # will errback and this code will never run. In other words, if we
            # get here, the subscriber is good.
            if is_valid:
                log.msg("Authenticating subscriber %s" % (self.transport.getPeer(),))
                self.authenticated = True
            else:
                log.warn("Authentication failed for %s" % (self.transport.getPeer(),))
                self.transport.loseConnection()

        return check_sig(packet).addCallback(do_authenticate)

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
