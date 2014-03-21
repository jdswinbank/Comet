# Comet VOEvent Broker.
# Record a seen event in the eventdb
# John Swinbank, <swinbank@transientskp.org>.

from zope.interface import implementer
from ..icomet import IHandler

@implementer(IHandler)
class EventRecorder(object):
    """
    Record the SHA1 & timestamp of an event in the event database.
    """
    name = "event-recorder"

    def __init__(self, eventdb):
        self.eventdb = eventdb

    def __call__(self, event):
        self.eventdb.record_event(event)
