# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.python.usage import Options
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.application.internet import TCPServer

# Transport protocol definitions
from ..tcp.protocol import VOEventPublisherFactory
from .relay import RelayingVOEventReceiverFactory
from .relay import RelayingVOEventSubscriberFactory

# Broker support
from .ivorn_db import IVORN_DB

# Local configuration
from config import PUBLISHER_PORT
from config import RECEIVER_PORT
from config import BROKER_SUBSCRIBE_TO
from config import LOCAL_IVO
from config import IVORN_DB_ROOT

def get_broker_service():
    ivorn_db = IVORN_DB(IVORN_DB_ROOT)

    broker_service = MultiService()
    publisher_factory = VOEventPublisherFactory(LOCAL_IVO)
    TCPServer(PUBLISHER_PORT, publisher_factory).setServiceParent(broker_service)

    receiver_factory = RelayingVOEventReceiverFactory(
        LOCAL_IVO,
        publisher_factory,
        ivorn_db
    )
    TCPServer(RECEIVER_PORT, receiver_factory).setServiceParent(broker_service)

    for host, port in BROKER_SUBSCRIBE_TO:
        log.msg("Subscribing to %s:%d" % (host, port))
        TCPClient(
            host, port,
            RelayingVOEventSubscriberFactory(LOCAL_IVO, publisher_factory, ivorn_db)
        ).setServiceParent(broker_service)
    return broker_service

def makeService(config):
    return get_broker_service()
