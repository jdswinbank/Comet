# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys
import datetime

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.internet import task

# Transport protocol definitions
from tcp.protocol import VOEventSubscriber
from tcp.protocol import VOEventPublisher, VOEventPublisherFactory
from tcp.protocol import VOEventReceiver, VOEventReceiverFactory

# Local configuration
from config import RECEIVER_LISTEN_ON
from config import PUBLISHER_LISTEN_ON
from config import LOCAL_IVO

def publish_event(protocol, event):
    for publisher in protocol.factory.publisher_factory.publishers:
        publisher.sendEvent(event)

class RelayingVOEventReceiverFactory(VOEventReceiverFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo, publisher_factory, handlers=[]):
        VOEventReceiverFactory.__init__(self, local_ivo)
        self.publisher_factory = publisher_factory
        self.handlers = handlers

if __name__ == "__main__":
    log.startLogging(sys.stdout)

    publisher_endpoint = serverFromString(reactor, PUBLISHER_LISTEN_ON)
    publisher_factory = VOEventPublisherFactory(LOCAL_IVO)
    publisher_endpoint.listen(publisher_factory)

    receiver_endpoint = serverFromString(reactor, RECEIVER_LISTEN_ON)
    receiver_factory = RelayingVOEventReceiverFactory(
        LOCAL_IVO,
        publisher_factory,
        [publish_event]
    )
    receiver_endpoint.listen(receiver_factory)

    reactor.run()
