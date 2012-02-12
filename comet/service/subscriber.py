# Comet VOEvent subscriber.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import lxml.etree as ElementTree

# Twisted
from twisted.internet import reactor
from twisted.python import log
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.plugin import getPlugins

# VOEvent transport protocol
from ..tcp.protocol import VOEventSubscriberFactory
from ..config.options import BaseOptions

# Handlers and plugins
import comet.plugins
from ..icomet import IHandler
from ..utility.spawn import SpawnCommand

class Options(BaseOptions):
    optParameters = [
        ["host", "h", "localhost", "Host to subscribe to."],
        ["port", "p", 8099, "Port to subscribe to.", int],
        ["filter", "f", None, "XPath expression."],
        ["action", None, None, "Add an event handler."],
        ["cmd", None, None, "Spawn external command on event receipt."]
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['filters'] = []
        self['actions'] = []
        self['handlers'] = []

    def opt_filter(self, my_filter):
        self['filters'].append(my_filter)

    def opt_action(self, action):
        self['actions'].append(action)

    def opt_cmd(self, cmd):
        self["handlers"].append(SpawnCommand(cmd))

    def postOptions(self):
        all_plugins = list(getPlugins(IHandler, comet.plugins))
        if not self['actions']:
            self['actions'] = [plugin.name for plugin in all_plugins]
        for plugin in all_plugins:
            if plugin.name in self['actions']:
                reactor.callWhenRunning(log.msg, "Adding action %s" % (plugin.name))
                self['handlers'].append(plugin)
                self['actions'].remove(plugin.name)
        for action in self['actions']:
            reactor.callWhenRunning(log.err, "Action %s not available" % (action))

def makeService(config):
    subscriber_service = MultiService()
    TCPClient(
        config['host'],
        config['port'],
        VOEventSubscriberFactory(
            config['local-ivo'],
            handlers=config['handlers'],
            filters=config['filters']
        )
    ).setServiceParent(subscriber_service)
    return subscriber_service
