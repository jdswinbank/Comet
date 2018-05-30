# Comet VOEvent Broker.
# Tests for VOEvent receiver.

import lxml.etree as etree

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from comet.testutils import DUMMY_VOEVENT, DUMMY_SERVICE_IVOID

from comet.protocol.receiver import VOEventReceiver, VOEventReceiverFactory

class VOEventReceiverFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventReceiverFactory(DUMMY_SERVICE_IVOID)

    def test_protocol(self):
        self.assertEqual(self.factory.protocol, VOEventReceiver)

    def test_contents(self):
        self.assertEqual(self.factory.local_ivo, DUMMY_SERVICE_IVOID)
        self.assertFalse(self.factory.validators) # Should be empty
        self.assertFalse(self.factory.handlers)   # Should be empty

class VOEventReceiverTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventReceiverFactory(DUMMY_SERVICE_IVOID)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_receive_unparsable(self):
        # An unparsable message should generate no response, but the
        # transport should disconnect.
        self.tr.clear()
        unparsable = b"This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.value(), b"")
        self.assertEqual(self.tr.connected, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should disconnect.
        self.tr.clear()
        incomprehensible = b"<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), b"")
        self.assertEqual(self.tr.connected, False)

    def test_receive_voevent(self):
        self.tr.clear()
        self.proto.stringReceived(DUMMY_VOEVENT)
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "ack"
        )
        self.assertEqual(self.tr.connected, False)

    def test_receive_voevent_invalid(self):
        def fail(event):
            raise Exception("Invalid")
        self.factory.validators.append(fail)
        self.tr.clear()
        self.proto.stringReceived(DUMMY_VOEVENT)
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "nak"
        )
        self.assertEqual(self.tr.connected, False)

    def test_timeout(self):
        self.clock.advance(self.proto.TIMEOUT)
        self.assertEqual(self.tr.connected, False)
