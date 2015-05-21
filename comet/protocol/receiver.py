# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@princeton.edu>, 2011-15.

import tarfile
from StringIO import StringIO

# Twisted protocol definition
from twisted.internet import defer
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import ServerFactory

# Base protocol definitions
from .base import EventHandler, VOEVENT_ROLES

# Comet utility routines
from ..utility import log
from ..utility.xml import xml_document, ParseError

class VOEventReceiver(EventHandler, TimeoutMixin):
    """
    A receiver waits for a one-shot submission from a connecting client.
    """
    TIMEOUT = 20 # Drop the connection if we hear nothing in TIMEOUT seconds.

    def connectionMade(self):
        log.msg("New connection from %s" % str(self.transport.getPeer()))
        self.setTimeout(self.TIMEOUT)

    def connectionLost(self, *args):
        # Don't leave the reactor in an unclean state when we exit.
        self.setTimeout(None)
        return EventHandler.connectionLost(self, *args)

    def timeoutConnection(self):
        log.msg(
            "%s timed out after %d seconds" %
            (str(self.transport.getPeer()), self.TIMEOUT)
        )
        return TimeoutMixin.timeoutConnection(self)

    def stringReceived(self, data):
        raise NotImplementedError

    def eventTextReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = xml_document(data)
        except ParseError:
            d = log.warning("Unparsable message received from %s" % str(self.transport.getPeer()))
        else:
            # The root element of both VOEvent and Transport packets has a
            # "role" element which we use to identify the type of message we
            # have received.
            if incoming.get('role') in VOEVENT_ROLES:
                log.msg(
                    "VOEvent %s received from %s" % (
                        incoming.attrib['ivorn'],
                        str(self.transport.getPeer())
                    )
                )
                d = self.process_event(incoming)
            else:
                d = log.warning(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.get("role"))
                )
        finally:
            return d

class VOEventReceiverFactory(ServerFactory):
    def __init__(self, local_ivo, validators=None, handlers=None):
        self.local_ivo = local_ivo
        self.validators = validators or []
        self.handlers = handlers or []

class SingleReceiver(VOEventReceiver):
    def stringReceived(self, data):
        log.debug("Single submission received from %s" % str(self.transport.getPeer()))
        return self.eventTextReceived(data).addCallback(
            lambda x: self.transport.loseConnection()
        )

class SingleReceiverFactory(VOEventReceiverFactory):
    protocol = SingleReceiver

class BulkReceiver(VOEventReceiver):
    """
    We expect a (possibly compressed) tarball of VOEvents. Iterate over the
    contents and dispatch each event to our subscribers.
    """
    MAX_LENGTH = 1000000000
    TIMEOUT = 200 # Drop the connection if we hear nothing in TIMEOUT seconds.

    def stringReceived(self, data):
        log.debug("Bulk submission received from %s" % str(self.transport.getPeer()))
        # Warning: blocks until we've processed this tarball
        return self.process_events(data)

    def process_events(self, data):
        tar = tarfile.open(fileobj=StringIO(data))
        return defer.gatherResults(
            self.eventTextReceived(tar.extractfile(member).read())
            for member in tar.getmembers()
            if member.isfile()
        ).addCallback(
            lambda x: self.transport.loseConnection()
        )

class BulkReceiverFactory(VOEventReceiverFactory):
    protocol = BulkReceiver
