# Comet VOEvent Broker.
# Check OpenPGP signatures.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from twisted.internet.threads import deferToThread

from zope.interface import implementer
from ..icomet import IValidator

from ..log import log

@implementer(IValidator)
class CheckSignature(object):
    def __call__(self, event):
        def check_validity(is_valid):
            if is_valid:
                log.debug("Event has good signature")
                return True
            else:
                log.debug("Signature could not be verified")
                raise Exception("Event signature invalid")

        def signature_failure(failure):
            log.warning("Unable to check signature")
            log.err(failure)
            return failure

        return deferToThread(
            event.valid_signature
        ).addCallbacks(check_validity, signature_failure)
