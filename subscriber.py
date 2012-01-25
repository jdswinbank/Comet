# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys
import lxml.etree as ElementTree

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString

# VOEvent transport protocol
from tcp.protocol import VOEventSubscriberFactory

# Local configuration
from config import LOCAL_IVO
from config import SUBSCRIBER_HOST
from config import SUBSCRIBER_PORT

def print_event(protocol, event):
    print ElementTree.tostring(event)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    reactor.connectTCP(
        SUBSCRIBER_HOST,
        SUBSCRIBER_PORT,
        VOEventSubscriberFactory(LOCAL_IVO, [print_event])
    )
    reactor.run()
