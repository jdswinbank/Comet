# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.internet import defer
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ReconnectingClientFactory

# Constructors for transport protocol messages
from .messages import Ack, Nak, IAmAlive, IAmAliveResponse
from .utils import serialize_element_to_xml


# Constants
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

"""
Implements the VOEvent Transport Protocol; see
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

All messages consist of a 4-byte network ordered payload size followed by the
payload data. Twisted's Int32StringReceiver handles this for us automatically.

There are four different VOEvent protocols to implement:

* VOEventSubscriber

    * Opens connection to remote broker, receives VOEvent messages.

* VOEventPublisher

    * Listens for connections from subscribers, sends VOEvent messages.

* VOEventSender

    * Connects to VOEventReceiver and publishes a new message.

* VOEventReceiver

    * Receives messages from VOEventSender.

To implement the broker, we need the Subscriber, Publisher & Receiver, but not
the Sender. All four are implemented here for completeness.
"""

class EventHandler(Int32StringReceiver):
    """
    Superclass for protocols which will receive events (ie, Subscriber and
    Receiver) providing event handling support.
    """
    def handle_event(self, event):
        """
        Call a set of event handlers on a given event (itself an ElementTree
        element).

        We return a DeferredList which fires when all handlers have run.
        """
        return defer.gatherResults(
            [
                defer.maybeDeferred(handler, self, event)
                for handler in self.factory.handlers
            ],
            consumeErrors=True
        )

class VOEventSubscriber(EventHandler):
    def stringReceived(self, data):
        """
        Called when a complete new message is received.

        We have two jobs here:

        1. Reply according to the Transport Protocol.
        2. Call a local event handler, voEventHandler(), defined in subclass.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received from %s" % str(self.transport.getPeer()))
            self.sendString(
                IAmAliveResponse(self.factory.local_ivo, incoming.find('Origin').text).to_string()
            )
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received from %s" % str(self.transport.getPeer()))
            self.sendString(
                Ack(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
            )
            self.handle_event(incoming).addCallbacks(
                lambda x: log.msg("Event processed"),
                lambda x: log.err("Event handlers failed")
            )
        else:
            log.err("Incomprehensible data received")

class VOEventSubscriberFactory(ReconnectingClientFactory):
    protocol = VOEventSubscriber

    def __init__(self, local_ivo, handlers=[]):
        self.local_ivo = local_ivo
        self.handlers = handlers

    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol()
        p.factory = self
        return p


class VOEventPublisher(Int32StringReceiver):
    MAX_ALIVE_COUNT = 1      # Drop connection if peer misses too many iamalives
    MAX_OUTSTANDING_ACK = 10 # Drop connection if peer misses too many acks

    def connectionMade(self):
        self.factory.publishers.append(self)
        self.alive_count = 0
        self.outstanding_ack = 0

    def connectionLost(self, reason):
        self.factory.publishers.remove(self)

    def sendIAmAlive(self):
        if self.alive_count > self.MAX_ALIVE_COUNT:
            log.msg("Peer appears to be dead; dropping connection")
            self.transport.loseConnection()
        elif self.outstanding_ack > self.MAX_OUTSTANDING_ACK:
            log.msg("Peer is not acknowledging events; dropping connection")
            self.transport.loseConnection()
        else:
            self.sendString(IAmAlive(self.factory.local_ivo).to_string())
            self.alive_count += 1

    def sendEvent(self, event):
        # event is an ElementTree element
        self.sendString(serialize_element_to_xml(event))
        self.outstanding_ack += 1
        log.msg("Sent event to %s" % str(self.transport.getPeer()))

    def stringReceived(self, data):
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received from %s" % str(self.transport.getPeer()))
            self.alive_count -= 1
        elif incoming.get('role') == "ack":
            log.msg("Ack received from %s" % str(self.transport.getPeer()))
            self.outstanding_ack -= 1
        elif incoming.get('role') == "nak":
            log.msg("Nak received from %s; terminating" % str(self.transport.getPeer()))
            self.transport.loseConnection()
        else:
            log.err(incoming.get('role'))
            log.err("Incomprehensible data received from %s" % str(self.transport.getPeer()))


class VOEventPublisherFactory(ServerFactory):
    IAMALIVE_INTERVAL = 60 # Sent iamalive every IAMALIVE_INTERVAL seconds
    protocol = VOEventPublisher

    def __init__(self, local_ivo):
        self.local_ivo = local_ivo
        self.publishers = []
        self.alive_loop = LoopingCall(self.sendIAmAlive)
        self.alive_loop.start(self.IAMALIVE_INTERVAL)

    def sendIAmAlive(self):
        for publisher in self.publishers:
            publisher.sendIAmAlive()


class VOEventSender(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        log.msg("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received from %s" % str(self.transport.getPeer()))
            return

        if incoming.get('role') == "ack":
            log.msg("Acknowledgement received from %s" % str(self.transport.getPeer()))
        elif incoming.get('role') == "nak":
            log.err("Nak received: %s refused to accept VOEvent" % str(self.transport.getPeer()))
        else:
            log.err("Incomprehensible data received from %s" % str(self.transport.getPeer()))

        # After receiving a message, we shut down the connection.
        self.transport.loseConnection()

class VOEventSenderFactory(Factory):
    protocol = VOEventSender



class VOEventReceiver(EventHandler):
    """
    A receiver waits for a one-shot submission from a connecting client.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received from %s" % str(self.transport.getPeer()))
            return

        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received from %s" % str(self.transport.getPeer()))
            if self.validate_event(data):
                log.msg("VOEvent is valid")
                self.sendString(
                    Ack(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
                )
                self.handle_event(incoming).addCallbacks(
                    lambda x: log.msg("Event processed"),
                    lambda x: log.err("Event handlers failed")
                )
            else:
                log.msg("VOEvent is NOT valid")
                self.sendString(
                    Nak(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
                )
            self.transport.loseConnection()
        else:
            log.err("Incomprehensible data received from %s" % str(self.transport.getPeer()))

    def validate_event(self, event):
        return self.factory.validate_event(event)

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver

    def __init__(self, local_ivo, validate=False, handlers=[]):
        self.local_ivo = local_ivo
        self.handlers = handlers
        if validate:
            from lxml import etree
            self.schema = etree.XMLSchema(etree.parse(validate))

    def validate_event(self, event):
        if hasattr(self, "schema"):
            from lxml import etree
            return self.schema.validate(etree.fromstring(event))
        else:
            return True
