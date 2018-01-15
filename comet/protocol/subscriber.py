# Comet VOEvent Broker.
# VOEventSubscriber: subscribe to a stream of events from a broker.

# Twisted protocol definition
from twisted.internet import reactor
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import ReconnectingClientFactory

# Base protocol definitions
from comet.protocol.base import EventHandler, VOEVENT_ROLES

# Constructors for transport protocol messages
from comet.protocol.messages import iamaliveresponse, authenticateresponse

# Comet utility routines
import comet.log as log
from comet.utility import xml_document, ParseError

__all__ = ["VOEventSubscriberFactory"]

class VOEventSubscriber(EventHandler, TimeoutMixin):
    ALIVE_INTERVAL = 120 # If we get no traffic for ALIVE_INTERVAL seconds,
                         # assume our peer forgot us.
    def __init__(self, filters=[]):
        self.filters = filters

    def connectionMade(self, *args):
        self.setTimeout(self.ALIVE_INTERVAL)
        return EventHandler.connectionMade(self, *args)

    def connectionLost(self, *args):
        # Don't leave the reactor in an unclean state when we exit.
        self.setTimeout(None)
        return EventHandler.connectionLost(self, *args)

    def timeoutConnection(self):
        log.info(
            "No iamalive received from %s for %d seconds; disconecting" %
            (self.transport.getPeer(), self.ALIVE_INTERVAL),
            system="VOEventSubscriber"
        )
        return TimeoutMixin.timeoutConnection(self)

    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = xml_document(data)
        except ParseError:
            log.warn("Unparsable message received")
            return

        # Reset the timeout counter and wait another 120 seconds before
        # disconnecting due to inactivity.
        self.resetTimeout()

        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.element.get('role') == "iamalive":
            log.debug("IAmAlive received from %s" % str(self.transport.getPeer()))
            self.send_xml(
                iamaliveresponse(self.factory.local_ivo,
                incoming.element.find('Origin').text)
            )
        elif incoming.element.get('role') == "authenticate":
            log.debug("Authenticate received from %s" % str(self.transport.getPeer()))
            self.send_xml(
                authenticateresponse(
                    self.factory.local_ivo,
                    incoming.element.find('Origin').text,
                    self.filters
                )
            )
        elif incoming.element.get('role') in VOEVENT_ROLES:
            log.info(
                "VOEvent %s received from %s" % (
                    incoming.element.attrib['ivorn'],
                    str(self.transport.getPeer())
                )
            )
            # We don't send a NAK even if the event is invalid since we don't
            # want to be removed from upstream's distribution list.
            self.process_event(incoming, can_nak=False)
        else:
            log.warn(
                "Incomprehensible data received from %s (role=%s)" %
                (self.transport.getPeer(), incoming.element.get("role"))
            )

class VOEventSubscriberFactory(ReconnectingClientFactory):
    RESET_DELAY = 5 # Reset exponential backoff after connection survives for
                    # at least RESET_DELAY seconds
    protocol = VOEventSubscriber
    callLater = reactor.callLater # Can be replaced in test cases
    def __init__(self,
        local_ivo=None, validators=None, handlers=None, filters=None,
    ):
        self.local_ivo = local_ivo
        self.handlers = handlers or []
        self.validators = validators or []
        self.filters = filters or []
        # Calling resetDelay() now is not necessary, but we want
        # self.reset_call always to exist when we use it later
        self.reset_call = self.callLater(0, self.resetDelay)

    def buildProtocol(self, addr):
        self.reset_call = self.callLater(self.RESET_DELAY, self.resetDelay)
        p = self.protocol(self.filters)
        p.factory = self
        return p

    def stopFactory(self):
        if self.reset_call.active():
            self.reset_call.cancel()

    def clientConnectionFailed(self, connector, reason):
        log.info(
            "Connection to %s failed; will retry in %d second%s" %
            (connector.getDestination(), self.delay, "" if self.delay == 1 else "s"),
            system="VOEventSubscriberFactory"

        )
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        log.info(
            "Connection to %s lost; will retry in %d second%s" %
            (connector.getDestination(), self.delay, "" if self.delay == 1 else "s"),
            system="VOEventSubscriberFactory"
        )
        if self.reset_call.active():
            self.reset_call.cancel()
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
