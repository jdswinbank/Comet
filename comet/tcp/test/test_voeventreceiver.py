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

class VOEventReceiverTestCaseBase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventReceiverFactory(DUMMY_SERVICE_IVORN)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def _transport_connected(self, *args, **kwargs):
        self.assertTrue(self.tr.connected)

    def _transport_disconnected(self, *args, **kwargs):
        self.assertFalse(self.tr.connected)

    def _sent_nothing(self, *args, **kwargs):
        self.assertEqual(self.tr.value(), "")

    def _sent_ack(self, *args, **kwargs):
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "ack"
        )

    def _sent_nak(self, *args, **kwargs):
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "nak"
        )

class VOEventReceiverTestCase(VOEventReceiverTestCaseBase):
    def test_receive_unparseable(self):
        # An unparseable message should generate no response, but the
        # transport should disconnect.
        self.tr.clear()
        unparseable = "This is not parseable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparseable)
        d = self.proto.stringReceived(unparseable)
        d.addCallback(self._sent_nothing)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should disconnect.
        self.tr.clear()
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        d = self.proto.stringReceived(incomprehensible)
        d.addCallback(self._sent_nothing)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_voevent(self):
        self.tr.clear()
        d = self.proto.stringReceived(DUMMY_VOEVENT)
        d.addCallback(self._sent_ack)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_voevent_invalid(self):
        def fail(event):
            raise Exception("Invalid")
        self.factory.validators.append(fail)
        self.tr.clear()
        d = self.proto.stringReceived(DUMMY_VOEVENT)
        d.addCallback(self._sent_nak)
        d.addCallback(self._transport_disconnected)
        return d

    def test_timeout(self):
        self.clock.advance(self.proto.TIMEOUT)
        self._transport_disconnected()
