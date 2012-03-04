import lxml.etree as etree

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_VOEVENT
from ...test.support import DUMMY_SERVICE_IVORN

from ..protocol import VOEventReceiver
from ..protocol import VOEventReceiverFactory

class VOEventReceiverFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventReceiverFactory(DUMMY_SERVICE_IVORN)

    def test_protocol(self):
        self.assertEqual(self.factory.protocol, VOEventReceiver)

    def test_contents(self):
        self.assertEqual(self.factory.local_ivo, DUMMY_SERVICE_IVORN)
        self.assertFalse(self.factory.validators) # Should be empty
        self.assertFalse(self.factory.handlers)   # Should be empty

class VOEventReceiverTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventReceiverFactory(DUMMY_SERVICE_IVORN)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_receive_unparseable(self):
        # An unparseable message should generate no response, but the
        # transport should not disconnect.
        self.tr.clear()
        unparseable = "This is not parseable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparseable)
        self.proto.stringReceived(unparseable)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        self.tr.clear()
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), "")
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
