# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import os
import sys
import anydbm
import datetime
from contextlib import closing

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
from config import IVORN_DB_ROOT

def publish_event(protocol, event):
    if protocol.factory.ivorn_db.check_ivorn(event.attrib['ivorn']):
        log.msg("This is a new event; forwarding")
        for publisher in protocol.factory.publisher_factory.publishers:
            publisher.sendEvent(event)
    else:
        log.msg("This is a previously seen event; dropping")

class RelayingVOEventReceiverFactory(VOEventReceiverFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo, publisher_factory, ivorn_db, validate=False, handlers=[]):
        VOEventReceiverFactory.__init__(self, local_ivo, validate, handlers)
        self.publisher_factory = publisher_factory
        self.ivorn_db = ivorn_db


class IVORN_DB(object):
    def __init__(self, root):
        self.root = root

    def check_ivorn(self, ivorn):
        db_path, key = ivorn.split('//')[1].split('#')
        db_path = db_path.replace(os.path.sep, "_")
        with closing(anydbm.open(os.path.join(self.root, db_path), 'c')) as db:
            if db.has_key(key):
                return False # Should not forward
            else:
                db[key] = str(datetime.datetime.utcnow())
                return True # Ok to forward


if __name__ == "__main__":
    log.startLogging(sys.stdout)

    publisher_endpoint = serverFromString(reactor, PUBLISHER_LISTEN_ON)
    publisher_factory = VOEventPublisherFactory(LOCAL_IVO)
    publisher_endpoint.listen(publisher_factory)

    receiver_endpoint = serverFromString(reactor, RECEIVER_LISTEN_ON)
    receiver_factory = RelayingVOEventReceiverFactory(
        LOCAL_IVO,
        publisher_factory,
        IVORN_DB(IVORN_DB_ROOT),
        validate="http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd",
        handlers=[publish_event]
    )
    receiver_endpoint.listen(receiver_factory)

    reactor.run()
