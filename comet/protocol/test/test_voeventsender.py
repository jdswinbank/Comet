# Comet VOEvent Broker.
# Tests for VOEvent submission.

import lxml.etree as etree

from twisted.trial import unittest
from twisted.test import proto_helpers

from comet.testutils import DummyEvent, DUMMY_ACK, DUMMY_NAK

from comet.protocol.sender import VOEventSender, VOEventSenderFactory

class VOEventSenderFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.event = DummyEvent()
        self.factory = VOEventSenderFactory(self.event)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSender)

    def test_no_ack(self):
        self.assertEqual(self.factory.ack, False)

    def test_stored_event(self):
        self.assertEqual(self.factory.event, self.event)

class VOEventSenderTestCase(unittest.TestCase):
    def setUp(self):
        self.event = DummyEvent()
        self.factory = VOEventSenderFactory(self.event)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_connectionMade(self):
        self.assertEqual(self.tr.value()[4:], self.event.raw_bytes)

    def test_receive_unparsable(self):
        # An unparsable message should generate no response, but the
        # transport should not disconnect.
        unparsable = b"This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.ack, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        incomprehensible = b"<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.ack, False)

    def test_receive_ack(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.proto.stringReceived(DUMMY_ACK)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.ack, True)

    def test_receive_nak(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.proto.stringReceived(DUMMY_NAK)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.ack, False)
