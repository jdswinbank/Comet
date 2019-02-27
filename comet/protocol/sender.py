# Comet VOEvent Broker.
# VOEventSender: publish VOEvents to a broker.

# Twisted protocol definition
from twisted.internet.defer import Deferred

# Comet protocol definitions
from comet.protocol.base import ElementSender

# Comet utility routines
import comet.log as log
from comet.utility import xml_document, ParseError

__all__ = ["VOEventSender"]

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
    def __init__(self):
        ElementSender.__init__(self)
        self._sent_ivoids = {}

    def send_event(self, event):
        """Send a VOEvent message.

        Parameters
        ---------
        event : `~comet.utility.xml_document`
            The event packet to send.

        Returns
        -------
        d : `~twisted.internet.defer.Deferred`
            A `~twisted.interet.defer.Deferred` which will be fired when the
            event is acknowledged by the recipient.
        """
        def log_response(incoming):
            """Default action to take on receiving an acknowledgement.

            The result is logged, the connection is closed (per the VTP spec)
            and the incoming packet is passed on to the next callback in the
            chain (if any).

            Parameters
            ----------
            incoming : `comet.utility.xml_document`
                The acknowledgement received.

            Returns
            -------
            incoming : `comet.utility.xml_document`
                The acknowledgement received.

            Notes
            -----
            A NAK is not considered a failure (we do not call an errback).
            """
            if incoming.element.get('role') == "ack":
                log.info("ACK received: %s accepted VOEvent" %
                         str(self.transport.getPeer()))
            elif incoming.element.get('role') == "nak":
                log.warn("NAK received: %s refused to accept VOEvent (%s)" %
                    (
                        str(self.transport.getPeer()),
                        incoming.element.findtext("Meta/Result",
                                                  default="no reason given")
                    )
                )
            self.transport.loseConnection()
            return incoming

        outgoing_ivoid = event.element.attrib['ivorn']
        self.send_xml(event)
        d = Deferred().addCallback(log_response)
        self._sent_ivoids[outgoing_ivoid] = d
        return d

    def stringReceived(self, data):
        """
        Called when we receive a string.

        The sender should only ever receive an ack or a nak, after which it
        should disconnect.
        """
        log.debug("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = xml_document.infer_type(data)

            if incoming.role in ("ack", "nak"):
                d = self._sent_ivoids.pop(incoming.element.find("Origin").text)
                d.callback(incoming)
            else:
                log.warn(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.role)
                )

        except ParseError:
            log.warn("Unparsable message received from %s" % str(self.transport.getPeer()))
