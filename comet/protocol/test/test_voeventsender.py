# Comet VOEvent Broker.
# Tests for VOEvent submission.

import lxml.etree as etree

from twisted.test import proto_helpers
from twisted.trial import unittest

from comet.protocol.sender import VOEventSender
from comet.testutils import (DUMMY_VOEVENT, DUMMY_ACK,
                             DUMMY_NAK, DUMMY_EVENT_IVOID)
from comet.utility import VOEventMessage

class VOEventSenderTestCase(unittest.TestCase):
    def setUp(self):
        self.event = VOEventMessage(DUMMY_VOEVENT)
        self.proto = VOEventSender()
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_connectionMade(self):
        # Initiating a connection sends nothing.
        self.assertEqual(self.tr.value(), b'')

    def test_send_event(self):
        # Sending an event should cause the event to appear on the transport.
        self.proto.send_event(self.event)
        self.assertEqual(self.tr.value()[4:], self.event.raw_bytes)
        self.assertIn(self.event.ivoid, self.proto._sent_ivoids.keys())

    def test_receive_unparsable(self):
        # A message that cannot be parsed as XML at all should be ignored: no
        # data is sent, and the transport is not disconnected.
        unparsable = b"This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(self.tr.value(), b'')

    def test_receive_incomprehensible(self):
        # A message that is XML but is meaningless should be ignored: no
        # data is sent, and the transport is not disconnected.
        incomprehensible = b"<xml/>"
        etree.fromstring(incomprehensible)  # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(self.tr.value(), b'')

    def test_receive_unknown_ack(self):
        # An ACK for a message that we didn't sent should be ignored: no data
        # is sent, and the transport is not disconnected.
        self.assertNotIn(DUMMY_EVENT_IVOID.decode(),
                         self.proto._sent_ivoids.keys())
        self.proto.stringReceived(DUMMY_ACK)
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(self.tr.value(), b'')

    def test_receive_known_ack(self):
        # An ACK for a message that we did send causes us to shut down the
        # connection.
        self.proto.send_event(self.event)
        self.assertIn(DUMMY_EVENT_IVOID.decode(),
                      self.proto._sent_ivoids.keys())
        self.proto.stringReceived(DUMMY_ACK)
        self.assertEqual(self.tr.connected, False)

    def test_receive_unknown_nak(self):
        # A NAK for a message that we did send causes us to shut down the
        # connection.
        self.assertNotIn(DUMMY_EVENT_IVOID.decode(),
                         self.proto._sent_ivoids.keys())
        self.proto.stringReceived(DUMMY_NAK)
        self.assertEqual(self.tr.connected, True)

    def test_receive_known_nak(self):
        # A NAK for a message that we did send causes us to shut down the
        # connection.
        self.proto.send_event(self.event)
        self.assertIn(DUMMY_EVENT_IVOID.decode(),
                      self.proto._sent_ivoids.keys())
        self.proto.stringReceived(DUMMY_NAK)
        self.assertEqual(self.tr.connected, False)

    def test_chain_deferred(self):
        # When a messages is ACKed, our custom deferred should fire and be
        # passed the message received.
        def callback_fn(incoming):
            self.assertEqual(incoming.origin, DUMMY_EVENT_IVOID.decode())

        d = self.proto.send_event(self.event)
        d.addCallback(callback_fn)
        self.proto.stringReceived(DUMMY_ACK)

    def test_chain_deferred_nak(self):
        # When a messages is NAKed, our custom deferred should fire and be
        # passed the message received.
        def callback_fn(incoming):
            self.assertEqual(incoming.origin, DUMMY_EVENT_IVOID.decode())

        d = self.proto.send_event(self.event)
        d.addCallback(callback_fn)
        self.proto.stringReceived(DUMMY_NAK)
