# Comet VOEvent Broker.
# VOEventSender: publish VOEvents to a broker.

# Twisted protocol definition
from twisted.internet.protocol import ClientFactory

# Comet protocol definitions
from comet.protocol.base import ElementSender

# Comet utility routines
import comet.log as log
from comet.utility import xml_document, ParseError

__all__ = ["VOEventSenderFactory"]

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
        log.debug("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = xml_document(data)

            if incoming.element.get('role') == "ack":
                log.info("Acknowledgement received from %s" % str(self.transport.getPeer()))
                self.factory.ack = True
            elif incoming.element.get('role') == "nak":
                log.warn("Nak received: %s refused to accept VOEvent (%s)" %
                    (
                        str(self.transport.getPeer()),
                        incoming.element.findtext("Meta/Result", default="no reason given")
                    )
                )
            else:
                log.warn(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.element.get("role"))
                )

        except ParseError:
            log.warn("Unparsable message received from %s" % str(self.transport.getPeer()))

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
            log.info("Event was sent successfully")
        else:
            log.warn("Event was NOT sent successfully")
