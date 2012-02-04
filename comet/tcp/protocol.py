# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# XML parsing using lxml
import lxml.etree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ReconnectingClientFactory

# Constructors for transport protocol messages
from .messages import ack, nak, iamalive, iamaliveresponse

# Constructor for our perodic test events
from ..utility.voevent import dummy_voevent_message

from ..utility.xml import xml_document

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

class ElementSender(Int32StringReceiver):
    """
    Superclass for protocols which will send XML messages which must be
    deserialized from ET elements.
    """
    def send_xml(self, document):
        """
        Takes a document and sents it as XML.

        The document might be an ElementTree element, in which case we
        serialise it to a (pretty, UTF-8) string, or it might be an
        xml_document with original text, which we send directly.

        Returns a deferred which fires when the event is being sent.
        """
        def get_text(document):
            if hasattr(document, "original"):
                return document.original
            else:
                return deferToThread(
                    ElementTree.tostring,
                    document,
                    xml_declaration=True,
                    encoding="UTF-8",
                    pretty_print=True
                )
        defer.maybeDeferred(get_text, document).addCallback(self.sendString)

class EventHandler(Int32StringReceiver):
    """
    Superclass for protocols which will receive events (ie, Subscriber and
    Receiver) providing event handling support.
    """
    def validate_event(self, event):
        """
        Call a set of event validators on a given event (itself an ElementTree
        element).

        If a validator raises an exception (ie, calls an errback), the event
        is invalid. Otherwise, it's ok.
        """
        return defer.gatherResults(
            [
                defer.maybeDeferred(validator, self, event)
                for validator in self.factory.validators
            ],
            consumeErrors=True,
        )

    def handle_event(self, event):
        """
        Call a set of event handlers on a given event (itself an ElementTree
        element).
        """
        return defer.gatherResults(
            [
                defer.maybeDeferred(handler, self, event)
                for handler in self.factory.handlers
            ],
            consumeErrors=True
        )

    def process_event(self, event):
        def handle_valid(status):
            self.send_xml(
                ack(self.factory.local_ivo, event.attrib['ivorn'])
            )
            self.handle_event(event).addCallbacks(
                lambda x: log.msg("Event processed"),
                lambda x: log.err("Event handlers failed")
            )

        def handle_invalid(failure):
            # Should unpack exception from failure to include useful output
            # in Nak
            self.send_xml(
                nak(self.factory.local_ivo, event.attrib['ivorn'])
            )
            log.msg("Event invalid; discarding")
        self.validate_event(event).addCallbacks(handle_valid, handle_invalid)


class VOEventSubscriber(EventHandler, ElementSender):
    ALIVE_INTERVAL = 120 # If we get no iamalive for ALIVE_INTERVAL seconds,
                         # assume our peer forgot us.
    def __init__(self):
        self.check_alive = reactor.callLater(self.ALIVE_INTERVAL, self.timed_out)

    def timed_out(self):
        log.msg(
            "No iamalive received for %d seconds; disconecting" %
            self.ALIVE_INTERVAL
        )
        self.transport.loseConnection()

    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = xml_document(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received from %s" % str(self.transport.getPeer()))
            self.check_alive.cancel()
            self.send_xml(
                iamaliveresponse(self.factory.local_ivo, incoming.find('Origin').text)
            )
            self.check_alive = reactor.callLater(self.ALIVE_INTERVAL, self.timed_out)
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg(
                "VOEvent %s received from %s" % (
                    incoming.attrib['ivorn'],
                    str(self.transport.getPeer())
                )
            )
            self.process_event(incoming)
        else:
            log.err("Incomprehensible data received")

class VOEventSubscriberFactory(ReconnectingClientFactory):
    protocol = VOEventSubscriber

    def __init__(self, local_ivo, validators=[], handlers=[]):
        self.local_ivo = local_ivo
        self.handlers = handlers
        self.validators = validators

    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol()
        p.factory = self
        return p


class VOEventPublisher(ElementSender):
    MAX_ALIVE_COUNT = 1      # Drop connection if peer misses too many iamalives
    MAX_OUTSTANDING_ACK = 10 # Drop connection if peer misses too many acks

    def connectionMade(self):
        log.msg("New subscriber at %s" % str(self.transport.getPeer()))
        self.factory.publishers.append(self)
        self.alive_count = 0
        self.outstanding_ack = 0

    def connectionLost(self, reason):
        log.msg("Subscriber at %s disconnected" % str(self.transport.getPeer()))
        self.factory.publishers.remove(self)

    def sendIAmAlive(self):
        if self.alive_count > self.MAX_ALIVE_COUNT:
            log.msg("Peer appears to be dead; dropping connection")
            self.transport.loseConnection()
        elif self.outstanding_ack > self.MAX_OUTSTANDING_ACK:
            log.msg("Peer is not acknowledging events; dropping connection")
            self.transport.loseConnection()
        else:
            self.send_xml(iamalive(self.factory.local_ivo))
            self.alive_count += 1

    def stringReceived(self, data):
        try:
            incoming = xml_document(data)
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
    TEST_INTERVAL = 3600   # Sent test event every TEST_INTERVAL seconds
    protocol = VOEventPublisher

    def __init__(self, local_ivo):
        self.local_ivo = local_ivo
        self.publishers = []
        self.alive_loop = LoopingCall(self.sendIAmAlive)
        self.alive_loop.start(self.IAMALIVE_INTERVAL)
        self.test_loop = LoopingCall(self.sendTestEvent)
        self.test_loop.start(self.TEST_INTERVAL)

    def sendIAmAlive(self):
        log.msg("Broadcasting iamalive")
        for publisher in self.publishers:
            publisher.sendIAmAlive()

    def sendTestEvent(self):
        log.msg("Broadcasting test event")
        test_event = dummy_voevent_message(self.local_ivo)
        for publisher in self.publishers:
            publisher.send_xml(test_event)


class VOEventSender(ElementSender):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.
    """
    def connectionMade(self):
        self.send_xml(self.factory.event)

    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        log.msg("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = xml_document(data)
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

class VOEventSenderFactory(ClientFactory):
    protocol = VOEventSender
    def __init__(self, event):
        self.event = event


class VOEventReceiver(EventHandler, ElementSender):
    """
    A receiver waits for a one-shot submission from a connecting client.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = xml_document(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received from %s" % str(self.transport.getPeer()))
            return

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
            self.process_event(incoming)
        else:
            log.err("Incomprehensible data received from %s" % str(self.transport.getPeer()))

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver

    def __init__(self, local_ivo, validators=[], handlers=[]):
        self.local_ivo = local_ivo
        self.validators = validators
        self.handlers = handlers
