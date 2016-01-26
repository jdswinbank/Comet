# Comet VOEvent Broker.
# Event relaying handler.

from zope.interface import implementer
from comet.icomet import IHandler

__all__ = ["EventRelay"]

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
