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
from .messages import ack, nak
from .messages import iamalive, iamaliveresponse
from .messages import authenticate, authenticateresponse

# Constructor for our perodic test events
from ..utility.voevent import broker_test_message

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

* VOEventBroadcaster

    * Listens for connections from subscribers, sends VOEvent messages.

* VOEventSender

    * Connects to VOEventReceiver and publishes a new message.

* VOEventReceiver

    * Receives messages from VOEventSender.

To implement the broker, we need the Subscriber, Broadcaster & Receiver, but not
the Sender. All four are implemented here for completeness.
"""

class ElementSender(Int32StringReceiver):
    """
    Superclass for protocols which will send XML messages which must be
    deserialized from ET elements.
    """
    def send_xml(self, document):
        """
        Takes an xml_document and sends it as text.
        """
        self.sendString(document.text)

    def lengthLimitExceeded(self, length):
        """
        This is called when a remote tries to send a massive string.

        Quite likely that's because it sends the prefix in little endian
        (rather than network) byte order.
        """
        log.msg("Length limit exceeded (%d bytes)." % (length,))
        Int32StringReceiver.lengthLimitExceeded(self, length)


class EventHandler(ElementSender):
    """
    Superclass for protocols which will receive events (ie, Subscriber and
    Receiver) providing event handling support.
    """
    def validate_event(self, event):
        """
        Call a set of event validators on a given event (an xml_document).

        If a validator raises an exception (ie, calls an errback), the event
        is invalid. Otherwise, it's ok.
        """
        return defer.gatherResults(
            [
                defer.maybeDeferred(validator, event)
                for validator in self.factory.validators
            ],
            consumeErrors=True
        )

    def handle_event(self, event):
        """
        Call a set of event handlers on a given event (itself an ElementTree
        element).
        """
        return defer.gatherResults(
            [
                defer.maybeDeferred(handler, event)
                for handler in self.factory.handlers
            ],
            consumeErrors=True
        )

    def process_event(self, event, can_nak=True):
        """
        Validate and (if appropriate) handle an event.

        If can_nak is False, we send an ACK (rather than a NAK) even if the
        event is invalid. This may be appropriate if we are a subscriber
        rather than a receiver: we should invalidate duplicate VOEvents
        received from multiple upstream brokers, but not respond to each with
        a NAK or they might shut off our connection as per the vTCP note (6.4
        -- "If there is an error (nak received...) [...] this would result in
        the broker removing the subscriber from its distribution list.
        """
        def handle_valid(status):
            # TODO: Check what happens if event handler fails. Can we call
            # another errback?
            log.msg("Sending ACK to %s" % (self.transport.getPeer()))
            self.send_xml(
                ack(self.factory.local_ivo, event.attrib['ivorn'])
            )
            self.handle_event(event).addCallbacks(
                lambda x: log.msg("Event processed"),
                lambda x: log.err("Event handlers failed")
            )

        def handle_invalid(failure):
            log.msg("Event rejected (%s); discarding" % (failure.value.subFailure.getErrorMessage(),))
            if can_nak:
                log.msg("Sending NAK to %s" % (self.transport.getPeer()))
                self.send_xml(
                    nak(
                        self.factory.local_ivo, event.attrib['ivorn'],
                        "Event rejected: %s" % (failure.value.subFailure.getErrorMessage(),)
                    )
                )
            else:
                log.msg("Sending ACK to %s" % (self.transport.getPeer()))
                self.send_xml(
                    ack(self.factory.local_ivo, event.attrib['ivorn'])
                )
        return self.validate_event(event).addCallbacks(handle_valid, handle_invalid)


class VOEventSubscriber(EventHandler):
    ALIVE_INTERVAL = 120 # If we get no iamalive for ALIVE_INTERVAL seconds,
                         # assume our peer forgot us.
    callLater = reactor.callLater
    def __init__(self, filters=[]):
        self.filters = filters

    def connectionMade(self, *args):
        self.check_alive = self.callLater(self.ALIVE_INTERVAL, self.timed_out)
        return EventHandler.connectionMade(self, *args)

    def connectionLost(self, *args):
        # Don't leave the reactor in an unclean state when we exit.
        if self.check_alive.active():
            self.check_alive.cancel()
        return EventHandler.connectionLost(self, *args)

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
        elif incoming.get('role') == "authenticate":
            log.msg("Authenticate received from %s" % str(self.transport.getPeer()))
            self.send_xml(
                authenticateresponse(
                    self.factory.local_ivo,
                    incoming.find('Origin').text,
                    self.filters
                )
            )
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg(
                "VOEvent %s received from %s" % (
                    incoming.attrib['ivorn'],
                    str(self.transport.getPeer())
                )
            )
            # We don't send a NAK even if the event is invalid since we don't
            # want to be removed from upstream's distribution list.
            self.process_event(incoming, can_nak=False)
        else:
            log.err(
                "Incomprehensible data received from %s (role=%s)" %
                (self.transport.getPeer(), incoming.get("role"))
            )

class VOEventSubscriberFactory(ReconnectingClientFactory):
    protocol = VOEventSubscriber

    def __init__(self, local_ivo, validators=[], handlers=[], filters=[]):
        self.local_ivo = local_ivo
        self.handlers = handlers
        self.validators = validators
        self.filters = filters

    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol(self.filters)
        p.factory = self
        return p

    def clientConnectionFailed(self, connector, reason):
        log.msg("Connection to %s failed; will retry" % (connector.getDestination(),))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        log.msg("Connection to %s lost; will retry" % (connector.getDestination(),))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


class VOEventBroadcaster(ElementSender):
    MAX_ALIVE_COUNT = 1      # Drop connection if peer misses too many iamalives
    MAX_OUTSTANDING_ACK = 10 # Drop connection if peer misses too many acks

    def __init__(self):
        self.filters = []

    def connectionMade(self):
        log.msg("New subscriber at %s" % str(self.transport.getPeer()))
        self.factory.broadcasters.append(self)
        self.alive_count = 0
        self.send_xml(authenticate(self.factory.local_ivo))
        self.outstanding_ack = 0

    def connectionLost(self, *args):
        log.msg("Subscriber at %s disconnected" % str(self.transport.getPeer()))
        self.factory.broadcasters.remove(self)
        return ElementSender.connectionLost(self, *args)

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
        elif incoming.get('role') == "authenticate":
            log.msg("Authentication received from %s" % str(self.transport.getPeer()))
            for xpath in incoming.findall("Meta/filter[@type=\"xpath\"]"):
                log.msg(
                    "Installing filter %s for %s" %
                    (xpath.text, str(self.transport.getPeer()))
                )
            self.filters = [
                ElementTree.XPath(xpath.text)
                for xpath in incoming.findall("Meta/filter[@type=\"xpath\"]")
            ]
        else:
            log.err(
                "Incomprehensible data received from %s (role=%s)" %
                (self.transport.getPeer(), incoming.get("role"))
            )

    def send_event(self, event):
        # Check the event against our filters and, if one or more pass, then
        # we send the event to our subscriber.
        def check_filters(result):
            if not self.filters or any([value for success, value in result if success]):
                log.msg("Event matches filter criteria: forwarding")
                self.send_xml(event)
            else:
                log.msg("Event rejected by filter")

        defer.DeferredList(
            [
                deferToThread(xpath, event.element)
                for xpath in self.filters
            ],
            consumeErrors=True,
        ).addCallback(check_filters)


class VOEventBroadcasterFactory(ServerFactory):
    IAMALIVE_INTERVAL = 60 # Sent iamalive every IAMALIVE_INTERVAL seconds
    TEST_INTERVAL = 3600   # Sent test event every TEST_INTERVAL seconds
    protocol = VOEventBroadcaster

    def __init__(self, local_ivo):
        self.local_ivo = local_ivo
        self.broadcasters = []
        self.alive_loop = LoopingCall(self.sendIAmAlive)
        self.alive_loop.start(self.IAMALIVE_INTERVAL)
        self.test_loop = LoopingCall(self.sendTestEvent)
        self.test_loop.start(self.TEST_INTERVAL)

    def sendIAmAlive(self):
        log.msg("Broadcasting iamalive")
        for broadcaster in self.broadcasters:
            broadcaster.sendIAmAlive()

    def sendTestEvent(self):
        log.msg("Broadcasting test event")
        test_event = broker_test_message(self.local_ivo)
        for broadcaster in self.broadcasters:
            broadcaster.send_event(test_event)


class VOEventSender(ElementSender):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.

    The sender connects to a remote host, sends a message, waits for an
    acknowledgement, and disconnects.
    """
    def connectionMade(self):
        self.send_xml(self.factory.event)

    def stringReceived(self, data):
        """
        Called when we receive a string.

        The sender should only ever receive an ack or a nak, after which it
        should disconnect.
        """
        log.msg("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = xml_document(data)

            if incoming.get('role') == "ack":
                log.msg("Acknowledgement received from %s" % str(self.transport.getPeer()))
                self.factory.ack = True
            elif incoming.get('role') == "nak":
                log.err("Nak received: %s refused to accept VOEvent (%s)" %
                    (
                        str(self.transport.getPeer()),
                        incoming.findtext("Meta/result", default="no reason given")
                    )
                )
            else:
                log.err(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.get("role"))
                )

        except ElementTree.ParseError:
            log.err("Unparsable message received from %s" % str(self.transport.getPeer()))

        finally:
            # After receiving a message, we shut down the connection.
            self.transport.loseConnection()

class VOEventSenderFactory(ClientFactory):
    protocol = VOEventSender
    def __init__(self, event):
        self.event = event
        self.ack = False

    def stopFactory(self):
        if self.ack:
            log.msg("Event was sent successfully")
        else:
            log.err("Event was NOT sent successfully")


class VOEventReceiver(EventHandler):
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
            log.err(
                "Incomprehensible data received from %s (role=%s)" %
                (self.transport.getPeer(), incoming.get("role"))
            )

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo, validators=[], handlers=[]):
        self.local_ivo = local_ivo
        self.validators = validators
        self.handlers = handlers
