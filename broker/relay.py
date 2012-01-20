# VOEvent Broker.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

from twisted.python import log
from tcp.protocol import VOEventReceiver, VOEventReceiverFactory

def publish_event(protocol, event):
    """
    Forward an event to all subscribers, unless we've seen the IVORN
    previously.
    """
    if protocol.factory.ivorn_db.check_ivorn(event.attrib['ivorn']):
        log.msg("This is a new event; forwarding")
        for publisher in protocol.factory.publisher_factory.publishers:
            publisher.sendEvent(event)
    else:
        log.msg("This is a previously seen event; dropping")

class RelayingVOEventReceiverFactory(VOEventReceiverFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo, publisher_factory, ivorn_db, validate=False):
        VOEventReceiverFactory.__init__(self, local_ivo, validate, [publish_event])
        self.publisher_factory = publisher_factory
        self.ivorn_db = ivorn_db
