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
from tcp.protocol import VOEventPublisherFactory
from broker.relay import RelayingVOEventReceiverFactory
from broker.relay import RelayingVOEventSubscriberFactory

# Broker support
from broker.ivorn_db import IVORN_DB

# Local configuration
from config import RECEIVER_LISTEN_ON
from config import PUBLISHER_LISTEN_ON
from config import LOCAL_IVO
from config import IVORN_DB_ROOT
from config import BROKER_SUBSCRIBE_TO

if __name__ == "__main__":
    log.startLogging(sys.stdout)

    ivorn_db = IVORN_DB(IVORN_DB_ROOT)

    publisher_endpoint = serverFromString(reactor, PUBLISHER_LISTEN_ON)
    publisher_factory = VOEventPublisherFactory(LOCAL_IVO)
    publisher_endpoint.listen(publisher_factory)

    receiver_endpoint = serverFromString(reactor, RECEIVER_LISTEN_ON)
    receiver_factory = RelayingVOEventReceiverFactory(
        LOCAL_IVO,
        publisher_factory,
        ivorn_db,
        validate="http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd",
    )
    receiver_endpoint.listen(receiver_factory)

    for host, port in BROKER_SUBSCRIBE_TO:
        log.msg("Subscribing to %s:%d" % (host, port))
        reactor.connectTCP(
            host, port,
            RelayingVOEventSubscriberFactory(
                LOCAL_IVO, publisher_factory, ivorn_db
            )
        )

    reactor.run()
