import lxml.etree as etree

from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DummyEvent
from ...test.support import DUMMY_ACK
from ...test.support import DUMMY_NAK

from ..protocol import VOEventSender
from ..protocol import VOEventSenderFactory

class VOEventSubscriberFactoryTestCase(unittest.TestCase):
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
        self.assertEqual(self.tr.value()[4:], self.event.text)

    def test_receive_unparseable(self):
        # An unparseable message should generate no response, but the
        # transport should not disconnect.
        unparseable = "This is not parseable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparseable)
        self.proto.stringReceived(unparseable)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.ack, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        incomprehensible = "<xml/>"
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
