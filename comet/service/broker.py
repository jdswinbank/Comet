# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import sys

# Used for building IP whitelist
from ipaddr import IPNetwork

# Twisted
from twisted.internet import reactor
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

class Options(BaseOptions):
    optParameters = [
        ["receiver-port", "r", 8098, "TCP port for receiving events.", int],
        ["subscriber-port", "p", 8099, "TCP port for publishing events.", int],
        ["ivorndb", "i", "/tmp", "IVORN database root."],
        ["whitelist", None, None, "Network to be included in submission whitelist (CIDR)."],
        ["remote", None, None, "Remote broker to subscribe to (host:port)."],
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['whitelist'] = []
        self['remotes'] = []

    def opt_whitelist(self, network):
        reactor.callWhenRunning(log.msg, "Accepting submissions from %s" % network)
        self['whitelist'].append(IPNetwork(network))

    def opt_remote(self, remote):
        reactor.callWhenRunning(log.msg, "Subscribing to remote broker %s" % remote)
        host, port = remote.split(":")
        self['remotes'].append((host, int(port)))


def makeService(config):
    ivorn_db = IVORN_DB(config['ivorndb'])

    broker_service = MultiService()
    publisher_factory = VOEventPublisherFactory(config["local-ivo"])
    TCPServer(
        config['subscriber-port'],
        publisher_factory
    ).setServiceParent(broker_service)

    TCPServer(
        config['receiver-port'],
        RelayingVOEventReceiverFactory(
            config["local-ivo"],
            publisher_factory,
            ivorn_db,
            config["whitelist"]
        )
    ).setServiceParent(broker_service)

    for host, port in config["remotes"]:
        TCPClient(
            host, port,
            RelayingVOEventSubscriberFactory(
                config["local-ivo"], publisher_factory, ivorn_db
            )
        ).setServiceParent(broker_service)
    return broker_service
