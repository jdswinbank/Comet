# Comet VOEvent Broker.
# VOEventBroadcaster: Listens for connections from subscribers,
# supplies them with VOEvent messages.

# Python standard library
from itertools import chain

# XML parsing using lxml
import lxml.etree as ElementTree

# Twisted protocol definition
from twisted.internet import defer
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet.protocol import ServerFactory

# Base protocol definitions
from comet.protocol.base import ElementSender

# Constructors for transport protocol messages
from comet.protocol.messages import iamalive, authenticate

# Comet utility routines
import comet.log as log
from comet.utility import broker_test_message, xml_document, ParseError

__all__ = ["VOEventBroadcasterFactory"]

class VOEventBroadcaster(ElementSender):
    MAX_ALIVE_COUNT = 1      # Drop connection if peer misses too many iamalives
    MAX_OUTSTANDING_ACK = 10 # Drop connection if peer misses too many acks

    def __init__(self):
        self.filters = []

    def connectionMade(self):
        log.info("New subscriber at %s" % str(self.transport.getPeer()))
        self.factory.broadcasters.append(self)
        self.alive_count = 0
        self.send_xml(authenticate(self.factory.local_ivo))
        self.outstanding_ack = 0

    def connectionLost(self, *args):
        log.info("Subscriber at %s disconnected" % str(self.transport.getPeer()))
        self.factory.broadcasters.remove(self)
        return ElementSender.connectionLost(self, *args)

    def sendIAmAlive(self):
        if self.alive_count >= self.MAX_ALIVE_COUNT:
            log.info("Peer appears to be dead; dropping connection")
            self.transport.loseConnection()
        elif self.outstanding_ack >= self.MAX_OUTSTANDING_ACK:
            log.info("Peer is not acknowledging events; dropping connection")
            self.transport.loseConnection()
        else:
            self.send_xml(iamalive(self.factory.local_ivo))
            self.alive_count += 1

    def stringReceived(self, data):
        try:
            incoming = xml_document(data)
        except ParseError:
            log.warn("Unparsable message received")
            return

        if incoming.element.get('role') == "iamalive":
            log.debug("IAmAlive received from %s" % str(self.transport.getPeer()))
            self.alive_count -= 1
        elif incoming.element.get('role') == "ack":
            log.debug("Ack received from %s" % str(self.transport.getPeer()))
            self.outstanding_ack -= 1
        elif incoming.element.get('role') == "nak":
            log.info("Nak received from %s; terminating" % str(self.transport.getPeer()))
            self.transport.loseConnection()
        elif incoming.element.get('role') == "authenticate":
            log.debug("Authentication received from %s" % str(self.transport.getPeer()))
            self.filters = []
            # Accept both "new-style" (<Param type="xpath-filter" />) and
            # old-style (<filter type="xpath" />) filters.
            for xpath in chain(
                [elem.get('value') for elem in incoming.element.findall("Meta/Param[@name=\"xpath-filter\"]")],
                [elem.text for elem in incoming.element.findall("Meta/filter[@type=\"xpath\"]")]
            ):
                log.info(
                    "Installing filter %s for %s" %
                    (xpath, str(self.transport.getPeer()))
                )
                try:
                    self.filters.append(ElementTree.XPath(xpath))
                except ElementTree.XPathSyntaxError:
                    log.info("Filter %s is not valid XPath" % (xpath,))
        else:
            log.warn(
                "Incomprehensible data received from %s (role=%s)" %
                (self.transport.getPeer(), incoming.element.get("role"))
            )

    def send_event(self, event):
        # Check the event against our filters and, if one or more pass, then
        # we send the event to our subscriber.
        def check_filters(result):
            if not self.filters or any([value for success, value in result if success]):
                log.info("Event matches filter criteria: forwarding to %s" % (str(self.transport.getPeer()),))
                self.send_xml(event)
                self.outstanding_ack += 1
            else:
                log.info("Event rejected by filter")

        return defer.DeferredList(
            [
                deferToThread(xpath, event.element)
                for xpath in self.filters
            ],
            consumeErrors=True,
        ).addCallback(check_filters)


class VOEventBroadcasterFactory(ServerFactory):
    IAMALIVE_INTERVAL = 60 # Sent iamalive every IAMALIVE_INTERVAL seconds
    protocol = VOEventBroadcaster

    def __init__(self, local_ivo, test_interval):
        # test_interval is the time in seconds between sending test events to
        # the network. 0 to disable.
        self.local_ivo = local_ivo
        self.test_interval = test_interval
        self.broadcasters = []
        self.alive_loop = LoopingCall(self.sendIAmAlive)
        self.test_loop = LoopingCall(self.sendTestEvent)

    def startFactory(self):
        self.alive_loop.start(self.IAMALIVE_INTERVAL)
        if self.test_interval:
            self.test_loop.start(self.test_interval)
        return ServerFactory.startFactory(self)

    def stopFactory(self):
        self.alive_loop.stop()
        if self.test_loop.running:
            self.test_loop.stop()
        return ServerFactory.stopFactory(self)

    def sendIAmAlive(self):
        log.debug("Broadcasting iamalive")
        for broadcaster in self.broadcasters:
            broadcaster.sendIAmAlive()

    def sendTestEvent(self):
        log.debug("Broadcasting test event")
        test_event = broker_test_message(self.local_ivo)
        for broadcaster in self.broadcasters:
            broadcaster.send_event(test_event)
