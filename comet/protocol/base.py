# Comet VOEvent Broker.
# Basic protocol building-blocks.

# Twisted protocol definition
from twisted.internet import defer
from twisted.protocols.basic import Int32StringReceiver

# Comet
import comet.log as log
from comet.protocol.messages import ack, nak

# Constants
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

class ElementSender(Int32StringReceiver):
    """
    Superclass for protocols which will send XML messages which must be
    deserialized from ET elements.
    """
    def send_xml(self, document):
        """
        Takes an xml_document and sends it as text.
        """
        self.sendString(document.raw_bytes)

    def lengthLimitExceeded(self, length):
        """
        This is called when a remote tries to send a massive string.

        Quite likely that's because it sends the prefix in little endian
        (rather than network) byte order.
        """
        log.info("Length limit exceeded (%d bytes)." % (length,))
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
        a NAK or they might shut off our connection as per the VTP note (6.4
        -- "If there is an error (nak received...) [...] this would result in
        the broker removing the subscriber from its distribution list.
        """
        def handle_valid(status):
            log.debug("Event accepted; sending ACK to %s" % (self.transport.getPeer()))
            self.send_xml(
                ack(self.factory.local_ivo, event.element.attrib['ivorn'])
            )
            self.handle_event(event).addCallbacks(
                lambda x: log.debug("Event processed"),
                lambda x: log.warn("Event handlers failed")
            )

        def handle_invalid(failure):
            log.info("Event rejected (%s); discarding" % (failure.value.subFailure.getErrorMessage(),))
            if can_nak:
                log.debug("Sending NAK to %s" % (self.transport.getPeer()))
                self.send_xml(
                    nak(
                        self.factory.local_ivo, event.element.attrib['ivorn'],
                        "Event rejected: %s" % (failure.value.subFailure.getErrorMessage(),)
                    )
                )
            else:
                log.debug("Sending ACK to %s" % (self.transport.getPeer()))
                self.send_xml(
                    ack(self.factory.local_ivo, event.element.attrib['ivorn'])
                )
        return self.validate_event(event).addCallbacks(handle_valid, handle_invalid)
