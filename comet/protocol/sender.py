# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@princeton.edu>, 2011-15.

import tarfile

# Twisted protocol definition
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import ClientFactory

# Comet utility routines
from ..utility import log
from ..utility.xml import xml_document, ParseError

class VOEventSender(Int32StringReceiver):
    """
    An abstract base for sending VOEvents.

    The VOEventSender will send some data to the remote host when a connection
    is made, then listen for one or more ack or nak packets. Once the total
    number of acks and naks has reached that defined in the factory, the
    connection is terminated.

    The data to be sent should be specified by subclassing and defining the
    outgoing_data property.
    """
    @property
    def outgoing_data(self):
        raise NotImplementedError

    def connectionMade(self):
        self.sendString(self.outgoing_data)

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


class SingleSender(VOEventSender):
    """
    Specialization of VOEventSender to send a single event, specified in the
    factory.
    """
    @property
    def outgoing_data(self):
        return self.factory.event.text


class SingleSenderFactory(VOEventSenderFactory):
    """
    Specialization of VOEventSenderFactory to send a single event. We always
    expect a single ack (or nak) in response.
    """
    protocol = SingleSender
    def __init__(self, event):
        VOEventSenderFactory.__init__(self)
        self.event = event
        self.responses_expected = 1

    def stopFactory(self):
        if self.acked == 1:
            log.msg("Event was sent successfully")
        else:
            log.warning("Event was NOT sent successfully")


class BulkSender(VOEventSender):
    """
    Specialization of VOEventSender to send a tarball containing multiple
    events. The tarball is read from the filesystem using a path stored in the
    factory.
    """
    @property
    def outgoing_data(self):
        with open(self.factory.tarball_path, 'rb') as f:
            return f.read()


class BulkSenderFactory(VOEventSenderFactory):
    """
    Specialization of VOEventSenderFactory to send a tarball of events. We
    estimate the number of responses expected based on the number of files
    in the tarball (but we don't check that they are actually VOEvents before
    sending, so this might not really be the number of responses received).
    """
    protocol = BulkSender
    def __init__(self, tarball_path):
        VOEventSenderFactory.__init__(self)
        self.tarball_path = tarball_path
        self.responses_expected = len(
            [x for x in tarfile.open(tarball_path).getmembers() if x.isfile()]
        )

    def stopFactory(self):
        log.msg("Received %d acks and %d naks" % (self.acked, self.naked))
