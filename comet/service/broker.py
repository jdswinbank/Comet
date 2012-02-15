# Comet VOEvent Broker.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import os

# Used for building IP whitelist
from ipaddr import IPNetwork

# Twisted
from twisted.internet import reactor
from twisted.python import log
from twisted.python import usage
from twisted.plugin import getPlugins
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.application.internet import TCPServer

# Comet broker routines
import comet
from ..config.options import BaseOptions
from ..tcp.protocol import VOEventPublisherFactory
from ..tcp.protocol import VOEventReceiverFactory
from ..tcp.protocol import VOEventSubscriberFactory
from ..utility.relay import EventRelay
from ..utility.whitelist import WhitelistingFactory
from ..utility.schemavalidator import SchemaValidator
from ..utility.ivorn_db import CheckPreviouslySeen
from ..utility.ivorn_db import IVORN_DB

# Handlers and plugins
import comet.plugins
from ..icomet import IHandler
from ..utility.spawn import SpawnCommand

class Options(BaseOptions):
    optFlags = [
        ["receiver", "r", "Listen for TCP connections from publishers."],
        ["publisher", "p", "Re-broadcast VOEvents received."]
    ]

    optParameters = [
        # General options
        ["ivorndb", None, "/tmp", "IVORN database root."],

        # Provide a publisher
        ["publisher-port", None, 8099, "TCP port for publishing events.", int],

        # Provide a receiver
        ["receiver-port", None, 8098, "TCP port for receiving events.", int],
        ["whitelist", None, "0.0.0.0/0", "Network to be included in submission whitelist."],

        # Subscribe to (potentially) multiple remote brokers
        ["remote", None, None, "Remote broker to subscribe to (host:port)."],
        ["filter", None, None, "XPath filter applied to events broadcast by remote."],

        # Actions taken when a new event is received
        ["action", None, None, "Add an event handler."],
        ["cmd", None, None, "Spawn external command on event receipt."]
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['remotes'] = []
        self['whitelist'] = []
        self['filters'] = []
        self['handlers'] = []

    def opt_action(self, action):
        plugin = [plugin for plugin in getPlugins(IHandler, comet.plugins) if plugin.name == action]
        if not plugin:
            reactor.callWhenRunning(log.err, "Action %s not available" % (action))
        else:
            self['handlers'].extend(plugin)

    def opt_cmd(self, cmd):
        self["handlers"].append(SpawnCommand(cmd))

    def opt_filter(self, my_filter):
        self['filters'].append(my_filter)

    def opt_remote(self, remote):
        reactor.callWhenRunning(log.msg, "Subscribing to remote broker %s" % remote)
        host, port = remote.split(":")
        self['remotes'].append((host, int(port)))

    def opt_whitelist(self, network):
        reactor.callWhenRunning(log.msg, "Whitelisting %s" % network)
        self['whitelist'].append(IPNetwork(network))

    def postOptions(self):
        if not (self['remotes'] or self['publisher'] or self['receiver']):
            reactor.callWhenRunning(log.err, "No services requested; stopping.")
            reactor.callWhenRunning(reactor.stop)


class WhitelistingReceiverFactory(VOEventReceiverFactory, WhitelistingFactory):
    def __init__(self, local_ivo, whitelist, validators=[], handlers=[]):
        VOEventReceiverFactory.__init__(self, local_ivo, validators, handlers)
        WhitelistingFactory.__init__(self, whitelist)


def makeService(config):
    ivorn_db = IVORN_DB(config['ivorndb'])

    broker_service = MultiService()
    if config['publisher']:
        publisher_factory = VOEventPublisherFactory(config["local-ivo"])
        TCPServer(
            config['publisher-port'],
            publisher_factory
        ).setServiceParent(broker_service)

        # If we're running a publisher, we will rebroadcast any events we
        # receive to it.
        config['handlers'].append(EventRelay(publisher_factory))

    if config['receiver']:
        TCPServer(
            config['receiver-port'],
            WhitelistingReceiverFactory(
                local_ivo=config["local-ivo"],
                whitelist=config["whitelist"],
                validators=[
                    CheckPreviouslySeen(ivorn_db),
                    SchemaValidator(
                        os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
                    )
                ],
                handlers=config['handlers']
            )
        ).setServiceParent(broker_service)

    for host, port in config["remotes"]:
        TCPClient(
            host, port,
            VOEventSubscriberFactory(
                local_ivo=config["local-ivo"],
                validators=[CheckPreviouslySeen(ivorn_db)],
                handlers=config['handlers'],
                filters=config['filters']
            )
        ).setServiceParent(broker_service)

    return broker_service
