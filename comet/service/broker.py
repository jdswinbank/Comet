# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import sys

# Used for building IP whitelist
from ipaddr import IPNetwork

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

class Options(BaseOptions):
    optParameters = [
        ["receiver-port", "r", 8098, "TCP port for receiving events.", int],
        ["subscriber-port", "p", 8099, "TCP port for publishing events.", int],
        ["ivorndb", "i", "/tmp", "IVORN database root."],
        ["remotes", None, "remotes.cfg", "Remote brokers to subscribe to."],
        ["whitelist", None, "whitelist.cfg", "Whitelist of hosts allowed to submit events."]
    ]

    def postOptions(self):
        try:
            with open(self["remotes"]) as f:
                self["remotes"] = [
                    (y, int(z)) for y, z in (
                        x.split("#")[0].split(":") for x in (
                            l.strip() for l in f.readlines()
                        ) if x[0] != "#"
                    )
                ] # Doncha love list comprehensions?
        except IOError:
            log.msg("Could not read list of remote brokers.")
            self["remotes"] = []

        try:
            with open(self["whitelist"]) as f:
                self["whitelist"] = [
                    IPNetwork(x.split("#")[0]) for x in (
                        l.strip() for l in f.readlines()
                    ) if x[0] != "#"
                ]
        except IOError:
            log.msg("Could not read list of remote brokers.")
        # If no whitelist is defined, we whitelist everything
        if not self["whitelist"]:
            self["whitelist"] = IPNetwork("0.0.0.0/0")

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
        log.msg("Subscribing to %s:%d" % (host, port))
        TCPClient(
            host, port,
            RelayingVOEventSubscriberFactory(
                config["local-ivo"], publisher_factory, ivorn_db
            )
        ).setServiceParent(broker_service)
    return broker_service
