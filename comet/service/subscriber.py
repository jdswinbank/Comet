# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys
import lxml.etree as ElementTree

# Twisted
from twisted.python import log
from twisted.python import usage
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient

# VOEvent transport protocol
from ..tcp.protocol import VOEventSubscriberFactory
from ..config.options import BaseOptions

class Options(BaseOptions):
    optParameters = [
        ["host", "h", "localhost", "Host to subscribe to."],
        ["port", "p", 8099, "Port to subscribe to."]
    ]

    def postOptions(self):
        self["port"] = int(self["port"])

def print_event(protocol, event):
    print ElementTree.tostring(event)

def makeService(config):
    subscriber_service = MultiService()
    TCPClient(
        config['host'],
        config['port'],
        VOEventSubscriberFactory(config['local_ivo'], [print_event])
    ).setServiceParent(subscriber_service)
    return subscriber_service
