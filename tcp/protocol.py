# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ReconnectingClientFactory

# Constructors for transport protocol messages
from .messages import Ack, Nak, IAmAlive, IAmAliveResponse

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

class VOEventSubscriber(Int32StringReceiver):
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

        We have two jobs here:

        1. Reply according to the Transport Protocol.
        2. Call a local event handler, voEventHandler(), defined in subclass.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received")
            self.sendString(
                IAmAliveResponse(self.factory.local_ivo, incoming.find('Origin').text).to_string()
            )
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            self.sendString(
                Ack(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
            )
            self.handle_event(incoming)
        else:
            log.err("Incomprehensible data received")

    def handle_event(self, event):
        for handler in self.factory.handlers:
            handler(self, event)

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
            log.msg("Sent iamalive %d" % self.alive_count)

    def sendEvent(self, event):
        self.sendString(ElementTree.tostring(event))
        self.outstanding_ack += 1
        log.msg("Sent event")

    def stringReceived(self, data):
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received")
            self.alive_count -= 1
        elif incoming.get('role') == "ack":
            log.msg("Ack received")
            self.outstanding_ack -= 1
        elif incoming.get('role') == "nak":
            log.msg("Nak received; terminating peer")
            self.transport.loseConnection()
        else:
            log.err(incoming.get('role'))
            log.err("Incomprehensible data received")


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
        log.msg("Got response")
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') == "ack":
            log.msg("Acknowledgement received")
        elif incoming.get('role') == "nak":
            log.err("Nak received: remote refused to accept VOEvent")
        else:
            log.err("Incomprehensible data received")

        # After receiving a message, we shut down the connection.
        self.transport.loseConnection()

class VOEventSenderFactory(Factory):
    protocol = VOEventSender


class VOEventReceiver(Int32StringReceiver):
    """
    When a VOEvent is received, we acknowledge it, shut down the connection,
    and call VOEventReceiver.voEventHandler() to process it. That method
    should be supplied in a subclass.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            if self.validate_event(data):
                log.msg("VOEvent is valid")
                self.sendString(
                    Ack(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
                )
                # Should use a deferred?
                self.handle_event(incoming)
            else:
                log.msg("VOEvent is NOT valid")
                self.sendString(
                    Nak(self.factory.local_ivo, incoming.attrib['ivorn']).to_string()
                )
            self.transport.loseConnection()
        else:
            log.err("Incomprehensible data received")

    def handle_event(self, event):
        for handler in self.factory.handlers:
            handler(self, event)

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
