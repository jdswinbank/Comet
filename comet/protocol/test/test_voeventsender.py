import lxml.etree as etree

from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DummyEvent, create_tar_string
from ...test.support import DUMMY_ACK, DUMMY_NAK

from ..sender import SingleSender, SingleSenderFactory
from ..sender import BulkSender, BulkSenderFactory

class GenericSenderFactoryTestCase(object):
    factory_type = None
    protocol_type = None

    def setUp(self):
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))

    def test_protocol(self):
        self.assertIsInstance(self.proto, self.protocol_type)

    def test_no_ack(self):
        self.assertEqual(self.factory.acked, 0)
        self.assertEqual(self.factory.naked, 0)


class SingleSenderFactoryTestCase(GenericSenderFactoryTestCase, unittest.TestCase):
    factory_type = SingleSenderFactory
    protocol_type = SingleSender

    def setUp(self):
        self.event = DummyEvent()
        self.factory = self.factory_type(self.event)
        GenericSenderFactoryTestCase.setUp(self)

    def test_stored_event(self):
        self.assertEqual(self.factory.event, self.event)


#class BulkSenderFactoryTestCase(GenericSenderFactoryTestCase, unittest.TestCase):
#    factory_type = BulkSenderFactory
#    protocol_type = BulkSender
#
#    def setUp(self):
#        self.factory = self.factory_type(self.event)
#        GenericSenderFactoryTestCase.setUp(self)
#
#    def test_stored_content(self):
#        # TODO: The bulk sender _factory_ should (probably?) read the whole
#        # tarfile into memory and provide that to the protocol, rather than just
#        # the path. Means the protocol doesn't have to handle file I/O, and makes
#        # the implementation of the test easier. Downside is that the whole
#        # tarball is sitting in memory until the factory is destroyed (but in
#        # practice, that's probably neither a big deal nor a significant
#        # regression)
#        pass


class SingleSenderTestCase(unittest.TestCase):
    def setUp(self):
        self.event = DummyEvent()
        self.factory = SingleSenderFactory(self.event)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_connectionMade(self):
        self.assertEqual(self.tr.value()[4:], self.event.text)

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
