import lxml.etree as etree

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_EVENT_IVORN as DUMMY_IVORN
from ...test.support import DUMMY_SERVICE_IVORN
from ...test.support import DUMMY_IAMALIVE
from ...test.support import DUMMY_AUTHENTICATE
from ...test.support import DUMMY_VOEVENT

from ..protocol import VOEventSubscriber
from ..protocol import VOEventSubscriberFactory

class VOEventSubscriberFactoryTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.makeConnection(proto_helpers.StringTransport())

    def tearDown(self):
        self.proto.connectionLost()

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSubscriber)


class VOEventSubscriberTimeoutTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_timeout(self):
        self.clock.advance(self.proto.ALIVE_INTERVAL)
        self.assertEqual(self.tr.connected, False)


class VOEventSubscriberTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_SERVICE_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        self.proto.connectionLost()

    def test_receive_unparseable(self):
        # An unparseable message should generate no response, but the
        # transport should not disconnect.
        unparseable = "This is not parseable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparseable)
        self.proto.stringReceived(unparseable)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.disconnecting, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.disconnecting, False)

    def test_receive_iamalive(self):
        self.proto.stringReceived(DUMMY_IAMALIVE)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("iamalive", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Response').text)

    def test_receive_authenticate(self):
        self.proto.stringReceived(DUMMY_AUTHENTICATE)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("authenticate", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Response').text)

    def test_receive_valid_voevent(self):
        self.proto.stringReceived(DUMMY_VOEVENT)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("ack", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Response').text)
        self.assertEqual(DUMMY_IVORN, received_element.find('Origin').text)

    def test_receive_invalid_voevent(self):
        # This should not be accepted, but *should not* generate a NAK.
        def invalid(event): raise Exception("Failed")
        self.proto.factory.validators.append(invalid)
        self.proto.stringReceived(DUMMY_VOEVENT)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("ack", received_element.attrib['role'])
        self.assertEqual(DUMMY_SERVICE_IVORN, received_element.find('Response').text)
        self.assertEqual(DUMMY_IVORN, received_element.find('Origin').text)
