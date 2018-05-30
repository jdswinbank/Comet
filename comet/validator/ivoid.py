# Comet VOEvent Broker.
# Check for valid IVOID.

from zope.interface import implementer
from comet.icomet import IValidator
from comet.utility import parse_ivoid

__all__ = ["CheckIVOID"]

@implementer(IValidator)
class CheckIVOID(object):
    """
    Check that the event received has an IVOID that corresponds to the
    description in "IVOA Identifiers Version 2.0" by Demleitner et al *and*
    provides a "local_ID" as per the VOEvent 2.0 spec (basically a fragment
    following a #).
    """
    def __call__(self, event):
        # parse_ivoid() raises if whatever it is passed is unparseable.
        auth, rsrc, local_ID = parse_ivoid(event.element.attrib['ivorn'])
        if not local_ID:
            raise Exception("No per-event local ID")
