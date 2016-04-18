# Comet VOEvent Broker.
# VOEventReceiver: Receive messages from authors.

# Twisted protocol definition
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import ServerFactory

# Base protocol definitions
from comet.protocol.base import EventHandler, VOEVENT_ROLES

# Comet utility routines
import comet.log as log
from comet.utility import xml_document, ParseError

__all__ = ["VOEventReceiverFactory"]

class VOEventReceiver(EventHandler, TimeoutMixin):
    """
    A receiver waits for a one-shot submission from a connecting client.
    """
    TIMEOUT = 20

    def connectionMade(self):
        log.info("New connection from %s" % str(self.transport.getPeer()))
        self.setTimeout(self.TIMEOUT)

    def connectionLost(self, *args):
        # Don't leave the reactor in an unclean state when we exit.
        self.setTimeout(None)
        return EventHandler.connectionLost(self, *args)

    def timeoutConnection(self):
        log.info(
            "%s timed out after %d seconds" %
            (str(self.transport.getPeer()), self.TIMEOUT)
        )
        return TimeoutMixin.timeoutConnection(self)

    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = xml_document(data)
        except ParseError:
            d = log.warn("Unparsable message received from %s" % str(self.transport.getPeer()))
        else:
            # The root element of both VOEvent and Transport packets has a
            # "role" element which we use to identify the type of message we
            # have received.
            if incoming.element.get('role') in VOEVENT_ROLES:
                log.info(
                    "VOEvent %s received from %s" % (
                        incoming.element.attrib['ivorn'],
                        str(self.transport.getPeer())
                    )
                )
                d = self.process_event(incoming)
            else:
                d = log.warn(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.element.get("role"))
                )
        finally:
            return d.addCallback(
                lambda x: self.transport.loseConnection()
            )


class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver

    def __init__(self, local_ivo, validators=None, handlers=None):
        self.local_ivo = local_ivo
        self.validators = validators or []
        self.handlers = handlers or []
