# Comet VOEvent subscriber.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import lxml.etree as ElementTree

# Twisted
from twisted.python import log
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient

# VOEvent transport protocol
from ..tcp.protocol import VOEventSubscriberFactory
from ..config.options import BaseOptions

class Options(BaseOptions):
    optParameters = [
        ["host", "h", "localhost", "Host to subscribe to."],
        ["port", "p", 8099, "Port to subscribe to.", int],
        ["filter", "f", None, "XPath expression."]
    ]

    def __init__(self):
        BaseOptions.__init__(self)
        self['filters'] = []

    def opt_filter(self, my_filter):
        self['filters'].append(my_filter)

def print_event(event):
    print ElementTree.tostring(event.element)

def makeService(config):
    subscriber_service = MultiService()
    TCPClient(
        config['host'],
        config['port'],
        VOEventSubscriberFactory(
            config['local-ivo'],
            handlers=[print_event],
            filters=config['filters']
        )
    ).setServiceParent(subscriber_service)
    return subscriber_service
