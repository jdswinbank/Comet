# Comet VOEvent Broker.
# Event relaying tools.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from twisted.python import log
from twisted.internet.protocol import ServerFactory

class EventRelay(object):
    """
    Forward an event to all subscribers.
    """
    def __init__(self, publisher_factory):
        self.publisher_factory = publisher_factory

    def __call__(self, protocol, event):
        for publisher in self.publisher_factory.publishers:
            publisher.send_event(event)
