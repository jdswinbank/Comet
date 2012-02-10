# Comet VOEvent Broker.
# Event relaying tools.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from twisted.python import log
from twisted.internet.protocol import ServerFactory

def publish_event(protocol, event):
    """
    Forward an event to all subscribers, unless we've seen the IVORN
    previously.
    """
    log.msg("Rebroadcasting event to subscribers")
    for publisher in protocol.factory.publisher_factory.publishers:
        publisher.send_event(event)

class RelayingFactory(ServerFactory):
    def __init__(self, publisher_factory, ivorn_db):
        self.publisher_factory = publisher_factory
        self.ivorn_db = ivorn_db
