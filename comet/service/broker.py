# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.python import usage
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.application.internet import TCPServer

# Transport protocol definitions
from ..config.options import BaseOptions
from ..tcp.protocol import VOEventPublisherFactory
from ..utility.relay import RelayingVOEventReceiverFactory
from ..utility.relay import RelayingVOEventSubscriberFactory

# Broker support
from ..utility.ivorn_db import IVORN_DB

# Local configuration
from config import BROKER_SUBSCRIBE_TO

class Options(BaseOptions):
    optParameters = [
        ["publisher_port", "p", 8099, "TCP port for publishing events."],
        ["receiver_port", "r", 8098, "TCP port for receiving events."],
        ["ivorndb", "i", "/tmp", "IVORN database root."]
    ]

    def postOptions(self):
        self["publisher_port"] = int(self["publisher_port"])
        self["receiver_port"] = int(self["receiver_port"])

def makeService(config):
    ivorn_db = IVORN_DB(config['ivorndb'])

    broker_service = MultiService()
    publisher_factory = VOEventPublisherFactory(config["local_ivo"])
    TCPServer(
        config['publisher_port'],
        publisher_factory
    ).setServiceParent(broker_service)

    TCPServer(
        config['receiver_port'],
        RelayingVOEventReceiverFactory(
            config["local_ivo"],
            publisher_factory,
            ivorn_db
        )
    ).setServiceParent(broker_service)

    for host, port in BROKER_SUBSCRIBE_TO:
        log.msg("Subscribing to %s:%d" % (host, port))
        TCPClient(
            host, port,
            RelayingVOEventSubscriberFactory(
                config["local_ivo"], publisher_factory, ivorn_db
            )
        ).setServiceParent(broker_service)
    return broker_service
