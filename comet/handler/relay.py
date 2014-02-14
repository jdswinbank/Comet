# Comet VOEvent Broker.
# Event relaying tools.
# John Swinbank, <swinbank@transientskp.org>.

from zope.interface import implementer
from ..icomet import IHandler

@implementer(IHandler)
class EventRelay(object):
    """
    Forward an event to all subscribers.
    """
    name = "event-relay"

    def __init__(self, broadcaster_factory):
        self.broadcaster_factory = broadcaster_factory

    def __call__(self, event):
        for broadcaster in self.broadcaster_factory.broadcasters:
            broadcaster.send_event(event)
