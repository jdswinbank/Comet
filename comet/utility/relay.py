# Comet VOEvent Broker.
# Event relaying tools.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from zope.interface import implements
from ..icomet import IHandler

class EventRelay(object):
    """
    Forward an event to all subscribers.
    """
    implements(IHandler)
    name = "event-relay"

    def __init__(self, publisher_factory):
        self.publisher_factory = publisher_factory

    def __call__(self, event):
        for publisher in self.publisher_factory.publishers:
            publisher.send_event(event)
