# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString

# VOEvent transport protocol
from tcp.protocol import VOEventSubscriber, VOEventSubscriberFactory

# Local configuration
from config import LOCAL_IVO
from config import SUBSCRIBER_CONNECT_TO

#class PrintingVOEventSubscriber(VOEventSubscriber):
#    def voEventHandler(self, event):
#        log.msg("Event received!")
#
#class PrintingVOEventSubscriberFactory(VOEventSubscriberFactory):
#    protocol = PrintingVOEventSubscriber

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = clientFromString(reactor, SUBSCRIBER_CONNECT_TO)
    endpoint.connect(VOEventSubscriberFactory(LOCAL_IVO))
    reactor.run()
