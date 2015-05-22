# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@princeton.edu>, 2011-15.

import tarfile
from StringIO import StringIO

# Twisted protocol definition
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import ClientFactory

# Comet utility routines
from ..utility import log
from ..utility.xml import xml_document, ParseError

class VOEventSender(Int32StringReceiver):
    """
    The VOEventSender will send some data to the remote host when a connection
    is made, then listen for one or more ack or nak packets. Once the total
    number of acks and naks has reached that defined in the factory, the
    connection is terminated.

    The data to be sent is read from the outgoing_data attribute of the
    factory.
    """
    def connectionMade(self):
        self.sendString(self.factory.outgoing_data)

    def stringReceived(self, data):
        log.debug("Got response from %s" % str(self.transport.getPeer()))
        try:
            incoming = xml_document(data)

            if incoming.get('role') == "ack":
                log.msg("Acknowledgement received from %s" % str(self.transport.getPeer()))
                self.factory.acked += 1
            elif incoming.get('role') == "nak":
                log.warning("Nak received: %s refused to accept VOEvent (%s)" %
                    (
                        str(self.transport.getPeer()),
                        incoming.findtext("Meta/Result", default="no reason given")
                    )
                )
                self.factory.naked += 1
            else:
                log.warning(
                    "Incomprehensible data received from %s (role=%s)" %
                    (self.transport.getPeer(), incoming.get("role"))
                )

        except ParseError:
            log.warning("Unparsable message received from %s" % str(self.transport.getPeer()))

        if (self.factory.acked + self.factory.naked) == self.factory.responses_expected:
            self.transport.loseConnection()


class VOEventSenderFactory(ClientFactory):
    """
    Abstract base factory for VOEvent sending clients.
    """
    def __init__(self):
        self.acked = 0
        self.naked = 0

    def stopFactory(self):
        log.msg("Received %d acks and %d naks" % (self.acked, self.naked))
        if self.acked != self.responses_expected:
            log.warning("Event sending unsuccessful")

class SingleSenderFactory(VOEventSenderFactory):
    """
    Specialization of VOEventSenderFactory to send a single event. We always
    expect a single ack (or nak) in response.
    """
    protocol = VOEventSender
    def __init__(self, event):
        VOEventSenderFactory.__init__(self)
        self.outgoing_data = event.text
        self.responses_expected = 1

class BulkSenderFactory(VOEventSenderFactory):
    """
    Specialization of VOEventSenderFactory to send a tarball of events. We
    estimate the number of responses expected based on the number of files
    in the tarball (but we don't check that they are actually VOEvents before
    sending, so this might not really be the number of responses received).
    """
    protocol = VOEventSender
    def __init__(self, tarball_path):
        VOEventSenderFactory.__init__(self)
        with open(tarball_path, 'rb') as f:
            self.outgoing_data = f.read()
        self.responses_expected = len(
            [
                x for x in
                tarfile.open(fileobj=StringIO(self.outgoing_data)).getmembers()
                if x.isfile()
            ]
        )
