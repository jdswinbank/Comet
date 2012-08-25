# Comet VOEvent Broker.
# Check OpenPGP signatures.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from zope.interface import implementer

from ..icomet import IValidator
from ..utility.auth import check_sig

@implementer(IValidator)
class CheckSignature(object):
    def __call__(self, event):
        def raise_if_invalid(result):
            if not result:
                raise Exception("Signature validation failed")
        return check_sig(event).addCallback(raise_if_invalid)
