import lxml.etree as etree

from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DummyEvent, temporary_tar
from ...test.support import DUMMY_ACK, DUMMY_NAK

from ..sender import VOEventSender
from ..sender import SingleSenderFactory, BulkSenderFactory

class GenericSenderFactoryTestCase(object):
    def setUp(self):
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSender)

    def test_no_ack(self):
        self.assertEqual(self.factory.acked, 0)
        self.assertEqual(self.factory.naked, 0)

    def test_stored_content(self):
        self.assertEqual(self.factory.outgoing_data, self.expected_data)


class SingleSenderFactoryTestCase(GenericSenderFactoryTestCase, unittest.TestCase):
    def setUp(self):
        event = DummyEvent()
        self.factory = SingleSenderFactory(event)
        self.expected_data = event.text
        GenericSenderFactoryTestCase.setUp(self)


class BulkSenderFactoryTestCase(GenericSenderFactoryTestCase, unittest.TestCase):
    def setUp(self):
        with temporary_tar([DummyEvent().text]) as tf:
            self.factory = BulkSenderFactory(tf)
            with open(tf, 'r') as f:
                self.expected_data = f.read()
        GenericSenderFactoryTestCase.setUp(self)


class VOEventSenderTestCase(object):
    def setUp(self):
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_connectionMade(self):
        self.assertEqual(self.tr.value()[4:], self.expected_outgoing)

    def test_receive_unparsable(self):
        # An unparsable message should generate no response, but the
        # transport should not disconnect.
        unparsable = "This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(self.factory.acked, 0)
        self.assertEqual(self.factory.naked, 0)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.connected, True)
        self.assertEqual(self.factory.acked, 0)
        self.assertEqual(self.factory.naked, 0)

    def test_receive_ack(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.proto.stringReceived(DUMMY_ACK)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.acked, 1)
        self.assertEqual(self.factory.naked, 0)

    def test_receive_nak(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.proto.stringReceived(DUMMY_NAK)
        self.assertEqual(self.tr.connected, False)
        self.assertEqual(self.factory.acked, 0)
        self.assertEqual(self.factory.naked, 1)


class SingleSenderTestCase(VOEventSenderTestCase, unittest.TestCase):
    def setUp(self):
        event = DummyEvent()
        self.expected_outgoing = event.text
        self.factory = SingleSenderFactory(event)
        VOEventSenderTestCase.setUp(self)


class BulkSenderTestCase(VOEventSenderTestCase, unittest.TestCase):
    def setUp(self):
        with temporary_tar([DummyEvent().text]) as tf:
            self.factory = BulkSenderFactory(tf)
            with open(tf, 'r') as f:
                self.expected_outgoing = f.read()
        VOEventSenderTestCase.setUp(self)
