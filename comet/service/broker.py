# Comet VOEvent Broker.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
import os

# Used for building IP whitelist
from ipaddr import IPNetwork

# Twisted
from twisted.internet import reactor
from twisted.python import usage
from twisted.plugin import getPlugins
from twisted.internet.task import LoopingCall
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.application.internet import TCPServer

# Comet broker routines
import comet
from ..log import log
from ..config.options import BaseOptions
from ..tcp.protocol import VOEventBroadcasterFactory
from ..tcp.protocol import VOEventReceiverFactory
from ..tcp.protocol import VOEventSubscriberFactory
from ..utility.whitelist import WhitelistingFactory
from ..utility.relay import EventRelay
from ..utility.schemavalidator import SchemaValidator
from ..utility.event_db import CheckPreviouslySeen
from ..utility.event_db import Event_DB

# Handlers and plugins
import comet.plugins
from ..icomet import IHandler
from ..utility.spawn import SpawnCommand

# Constants
MAX_AGE = 30.0 * 24 * 60 * 60 # Forget events after 30 days
PRUNE_INTERVAL = 6 * 60 * 60  # Prune the event db every 6 hours
DEFAULT_REMOTE_PORT = 8099    # If the user doesn't specify

class Options(BaseOptions):
    optFlags = [
        ["receive", "r", "Listen for TCP connections from authors."],
        ["broadcast", "b", "Re-broadcast VOEvents received."],
        ["verbose", "v", "Increase verbosity."],
        ["quiet", "q", "Decrease verbosity."]
    ]

    optParameters = [
        ["eventdb", None, "/tmp", "Event database root."],
        ["receive-port", None, 8098, "TCP port for receiving events.", int],
        ["broadcast-port", None, 8099, "TCP port for broadcasting events.", int],
        ["whitelist", None, "0.0.0.0/0", "Network to be included in submission whitelist."],
        ["remote", None, None, "Remote broadcaster to subscribe to (host[:port])."],
        ["filter", None, None, "XPath filter applied to events broadcast by remote."],
        ["action", None, None, "Add an event handler."],
        ["cmd", None, None, "Spawn external command on event receipt."]
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['remotes'] = []
        self['running_whitelist'] = []
        self['filters'] = []
        self['handlers'] = []
        self['verbosity'] = 1

    def opt_quiet(self):
        self['verbosity'] -= 1
    opt_q = opt_quiet

    def opt_verbose(self):
        self['verbosity'] += 1
    opt_v = opt_verbose

    def opt_action(self, action):
        plugin = [plugin for plugin in getPlugins(IHandler, comet.plugins) if plugin.name == action]
        if not plugin:
            reactor.callWhenRunning(log.warning, "Action %s not available" % (action))
        else:
            self['handlers'].extend(plugin)

    def opt_cmd(self, cmd):
        self["handlers"].append(SpawnCommand(cmd))

    def opt_filter(self, my_filter):
        self['filters'].append(my_filter)

    def opt_remote(self, remote):
        try:
            host, port = remote.split(":")
        except ValueError:
            host, port = remote, DEFAULT_REMOTE_PORT
        reactor.callWhenRunning(
            log.msg,
            "Subscribing to remote broker %s:%d" % (host, int(port))
        )
        self['remotes'].append((host, int(port)))

    def opt_whitelist(self, network):
        reactor.callWhenRunning(log.msg, "Whitelisting %s" % network)
        self['running_whitelist'].append(IPNetwork(network))

    def postOptions(self):
        if self['running_whitelist']:
            self['whitelist'] = self['running_whitelist']
        else:
            self['whitelist'] = [IPNetwork(self['whitelist'])]

        if self['verbosity'] >= 2:
            log.LEVEL = log.Levels.DEBUG
        elif self['verbosity'] == 1:
            log.LEVEL = log.Levels.INFO
        else:
            log.LEVEL = log.Levels.WARNING


def makeService(config):
    event_db = Event_DB(config['eventdb'])
    LoopingCall(event_db.prune, MAX_AGE).start(PRUNE_INTERVAL)

    broker_service = MultiService()
    if config['broadcast']:
        broadcaster_factory = VOEventBroadcasterFactory(config["local-ivo"])
        if log.LEVEL >= log.Levels.INFO: broadcaster_factory.noisy = False
        broadcaster_service = TCPServer(
            config['broadcast-port'],
            broadcaster_factory
        )
        broadcaster_service.setName("Broadcaster")
        broadcaster_service.setServiceParent(broker_service)

        # If we're running a broadcast, we will rebroadcast any events we
        # receive to it.
        config['handlers'].append(EventRelay(broadcaster_factory))

    if config['receive']:
        receiver_factory = VOEventReceiverFactory(
            local_ivo=config['local-ivo'],
            validators=[
                CheckPreviouslySeen(event_db),
                SchemaValidator(
                    os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
                )
            ],
            handlers=config['handlers']
        )
        if log.LEVEL >= log.Levels.INFO: receiver_factory.noisy = False
        whitelisting_factory = WhitelistingFactory(receiver_factory, config['whitelist'])
        if log.LEVEL >= log.Levels.INFO: whitelisting_factory.noisy = False
        receiver_service = TCPServer(config['receive-port'], whitelisting_factory)
        receiver_service.setName("Receiver")
        receiver_service.setServiceParent(broker_service)

    for host, port in config["remotes"]:
        subscriber_factory = VOEventSubscriberFactory(
            local_ivo=config["local-ivo"],
            validators=[CheckPreviouslySeen(event_db)],
            handlers=config['handlers'],
            filters=config['filters']
        )
        if log.LEVEL >= log.Levels.INFO: subscriber_factory.noisy = False
        remote_service = TCPClient(host, port, subscriber_factory)
        remote_service.setName("Remote %s:%d" % (host, port))
        remote_service.setServiceParent(broker_service)

    if not broker_service.services:
        reactor.callWhenRunning(log.warning, "No services requested; stopping.")
        reactor.callWhenRunning(reactor.stop)
    return broker_service
