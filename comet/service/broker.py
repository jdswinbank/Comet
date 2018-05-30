# Comet VOEvent Broker.
# Master broker service.

# Python standard library
import os

# Used for building IP whitelist
from ipaddress import ip_network

# lxml XML handling
from lxml.etree import XPath, XPathSyntaxError

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
import comet.log as log
from comet.protocol import VOEventBroadcasterFactory
from comet.protocol import VOEventReceiverFactory
from comet.protocol import VOEventSubscriberFactory
from comet.utility import Event_DB, BaseOptions, WhitelistingFactory
from comet.validator import CheckIVOID, CheckPreviouslySeen, CheckSchema

# Handlers and plugins
import comet.plugins
from comet.icomet import IHandler, IHasOptions
from comet.handler import SpawnCommand, EventRelay

# We only need export the items twistd needs to construct a service.
__all__ = ["makeService", "Options"]

# Constants
MAX_AGE = 30.0 * 24 * 60 * 60 # Forget events after 30 days
PRUNE_INTERVAL = 6 * 60 * 60  # Prune the event db every 6 hours
DEFAULT_REMOTE_PORT = 8099    # If the user doesn't specify

# By default, we brodcast a test event every BCAST_TEST_INTERVAL seconds.
BCAST_TEST_INTERVAL = 3600

class Options(BaseOptions):
    optFlags = [
        ["receive", "r", "Listen for TCP connections from authors."],
        ["broadcast", "b", "Re-broadcast VOEvents received."],
        ["verbose", "v", "Increase verbosity."],
        ["quiet", "q", "Decrease verbosity."]
    ]

    optParameters = [
        ["eventdb", None, os.environ.get("TMPDIR", "/tmp"), "Event database root."],
        ["receive-port", None, 8098, "TCP port for receiving events.", int],
        ["broadcast-port", None, DEFAULT_REMOTE_PORT, "TCP port for broadcasting events.", int],
        ["broadcast-test-interval", None, BCAST_TEST_INTERVAL, "Interval between test event brodcasts (in seconds; 0 to disable).", int],
        ["author-whitelist", None, "0.0.0.0/0", "Network to be included in author whitelist."],
        ["subscriber-whitelist", None, "0.0.0.0/0", "Network to be included in subscriber whitelist."],
        ["remote", None, None, "Remote broadcaster to subscribe to (host[:port])."],
        ["filter", None, None, "XPath filter applied to events broadcast by remote."],
        ["cmd", None, None, "Spawn external command on event receipt."]
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['remotes'] = []
        self['running_author-whitelist'] = []
        self['running_subscriber-whitelist'] = []
        self['filters'] = []
        self['handlers'] = []
        self['verbosity'] = 1

    def opt_quiet(self):
        self['verbosity'] -= 1
    opt_q = opt_quiet

    def opt_verbose(self):
        self['verbosity'] += 1
    opt_v = opt_verbose

    def opt_cmd(self, cmd):
        self["handlers"].append(SpawnCommand(cmd))

    def opt_filter(self, my_filter):
        try:
            # Weed out invalid filters
            XPath(my_filter)
        except XPathSyntaxError:
            raise usage.UsageError("Invalid XPath expression: %s" % my_filter)
        self['filters'].append(my_filter)

    def opt_remote(self, remote):
        try:
            host, port = remote.split(":")
        except ValueError:
            host, port = remote, DEFAULT_REMOTE_PORT
        reactor.callWhenRunning(
            log.info,
            "Subscribing to remote broker %s:%d" % (host, int(port))
        )
        self['remotes'].append((host, int(port)))

    def opt_author_whitelist(self, network):
        reactor.callWhenRunning(log.info, "Whitelisting %s for submission" % network)
        self['running_author-whitelist'].append(ip_network(network, strict=False))

    def opt_subscriber_whitelist(self, network):
        reactor.callWhenRunning(log.info, "Whitelisting %s for subscription" % network)
        self['running_subscriber-whitelist'].append(ip_network(network, strict=False))

    def postOptions(self):
        BaseOptions.postOptions(self)
        if self['running_author-whitelist']:
            self['author-whitelist'] = self['running_author-whitelist']
        else:
            self['author-whitelist'] = [ip_network(self['author-whitelist'], strict=False)]

        if self['running_subscriber-whitelist']:
            self['subscriber-whitelist'] = self['running_subscriber-whitelist']
        else:
            self['subscriber-whitelist'] = [ip_network(self['subscriber-whitelist'], strict=False)]

        if self['verbosity'] >= 2:
            log.LEVEL = log.Levels.DEBUG
        elif self['verbosity'] == 1:
            log.LEVEL = log.Levels.INFO
        else:
            log.LEVEL = log.Levels.WARNING

        # Now enable plugins if requested.
        # We loop over all plugins, checking if the user supplied their name
        # on the command line and adding them to our list of handlers if so.
        for plugin in getPlugins(IHandler, comet.plugins):
            if self[plugin.name]:
                if IHasOptions.providedBy(plugin):
                    for name, _, _ in plugin.get_options():
                        plugin.set_option(name, self["%s-%s" % (plugin.name, name)])
                self['handlers'].append(plugin)


# Stub the options for all our plugins into the option handler
for plugin in getPlugins(IHandler, comet.plugins):
    Options.optFlags.append(
        [plugin.name, None, "Enable the %s plugin." % (plugin.name,)]
    )
    if IHasOptions.providedBy(plugin):
        for name, default, description in plugin.get_options():
            Options.optParameters.append(
                ["%s-%s" % (plugin.name, name), None, default, description]
            )


def makeService(config):
    event_db = Event_DB(config['eventdb'])
    LoopingCall(event_db.prune, MAX_AGE).start(PRUNE_INTERVAL)

    broker_service = MultiService()
    if config['broadcast']:
        broadcaster_factory = VOEventBroadcasterFactory(
            config["local-ivo"], config['broadcast-test-interval']
        )
        if log.LEVEL >= log.Levels.INFO: broadcaster_factory.noisy = False
        broadcaster_whitelisting_factory = WhitelistingFactory(
            broadcaster_factory, config['subscriber-whitelist'], "subscription"
        )
        if log.LEVEL >= log.Levels.INFO: broadcaster_whitelisting_factory.noisy = False
        broadcaster_service = TCPServer(
            config['broadcast-port'],
            broadcaster_whitelisting_factory
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
                CheckSchema(
                    os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
                ),
                CheckIVOID()
            ],
            handlers=config['handlers']
        )
        if log.LEVEL >= log.Levels.INFO: receiver_factory.noisy = False
        author_whitelisting_factory = WhitelistingFactory(
            receiver_factory, config['author-whitelist'], "submission"
        )
        if log.LEVEL >= log.Levels.INFO: author_whitelisting_factory.noisy = False
        receiver_service = TCPServer(config['receive-port'], author_whitelisting_factory)
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
        reactor.callWhenRunning(log.warn, "No services requested; stopping.")
        reactor.callWhenRunning(reactor.stop)
    return broker_service
