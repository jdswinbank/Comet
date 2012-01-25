# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString

# VOEvent transport protocol
from tcp.protocol import VOEventSenderFactory

# Constructors for messages
from voevent.voevent import dummy_voevent_message

# Local configuration
from config import LOCAL_IVO
from config import SENDER_CONNECT_TO

class OneShotVOEventSenderFactory(VOEventSenderFactory):
    """
    Since we're just sending one event, we'll stop the reactor when our
    connection is done.
    """
    def stopFactory(self):
        reactor.stop()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = clientFromString(reactor, SENDER_CONNECT_TO)
    d = endpoint.connect(OneShotVOEventSenderFactory())
    d.addCallback(
        lambda proto: proto.send_element(dummy_voevent_message(LOCAL_IVO))
    )
    reactor.run()
