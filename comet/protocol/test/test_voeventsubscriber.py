# Comet VOEvent Broker.
# Tests for subscriber component.

import lxml.etree as etree

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from comet.testutils import (DUMMY_EVENT_IVOID, DUMMY_SERVICE_IVOID,
                             DUMMY_IAMALIVE, DUMMY_AUTHENTICATE,
                             DUMMY_VOEVENT)

from comet.protocol.subscriber import (VOEventSubscriber,
                                         VOEventSubscriberFactory)

class VOEventSubscriberFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.clock = task.Clock()
        self.factory = VOEventSubscriberFactory(DUMMY_EVENT_IVOID)
        self.factory.callLater = self.clock.callLater
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))

    def tearDown(self):
        self.proto.connectionLost()

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSubscriber)

    def test_reconnect_delay(self):
        # Retries and delay are not reset immediately on connection, but
        # rather only after RESET_DELAY seconds have passed.
        self.factory.retries = VOEventSubscriberFactory.retries + 1
        self.factory.delay = VOEventSubscriberFactory.delay + 1
        self.proto.makeConnection(self.transport)
        self.assertNotEqual(self.factory.retries, VOEventSubscriberFactory.retries)
        self.assertNotEqual(self.factory.delay, VOEventSubscriberFactory.delay)
        self.clock.advance(VOEventSubscriberFactory.RESET_DELAY)
        self.assertEqual(self.factory.retries, VOEventSubscriberFactory.retries)
        self.assertEqual(self.factory.delay, VOEventSubscriberFactory.delay)


class VOEventSubscriberTimeoutTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_EVENT_IVOID)
        self.clock = task.Clock()
        factory.callLater = self.clock.callLater
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.callLater = self.clock.callLater # Original in TimeoutMixin
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_timeout(self):
        self.clock.advance(self.proto.ALIVE_INTERVAL)
        self.assertEqual(self.tr.connected, False)


# Per the VTP spec, it's valid for subscribers either to have or not to have
# IVOIDs. If they do have them, though, they must be used properly. We run the
# same set of tests for both cases.

class VOEventSubscriberTestCase(object):
    # Abstract base for the with and without ID test cases, below.

    def setUp(self):
        factory = VOEventSubscriberFactory(self.IVOID)
        factory.callLater = task.Clock().callLater
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        self.proto.connectionLost()

    def test_receive_unparsable(self):
        # An unparsable message should generate no response, but the
        # transport should not disconnect.
        unparsable = b"This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.value(), b"")
        self.assertEqual(self.tr.disconnecting, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response, but the
        # transport should not disconnect.
        incomprehensible = b"<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), b"")
        self.assertEqual(self.tr.disconnecting, False)

    def test_receive_iamalive(self):
        self.proto.stringReceived(DUMMY_IAMALIVE)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("iamalive", received_element.attrib['role'])
        if self.IVOID:
            self.assertEqual(DUMMY_SERVICE_IVOID.decode(),
                             received_element.find('Response').text)

    def test_receive_authenticate(self):
        self.proto.stringReceived(DUMMY_AUTHENTICATE)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("authenticate", received_element.attrib['role'])
        if self.IVOID:
            self.assertEqual(DUMMY_SERVICE_IVOID.decode(),
                             received_element.find('Response').text)

    def test_receive_valid_voevent(self):
        self.proto.stringReceived(DUMMY_VOEVENT)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("ack", received_element.attrib['role'])
        if self.IVOID:
            self.assertEqual(DUMMY_SERVICE_IVOID.decode(),
                             received_element.find('Response').text)
        self.assertEqual(DUMMY_EVENT_IVOID.decode(),
                         received_element.find('Origin').text)

    def test_receive_invalid_voevent(self):
        # This should not be accepted, but *should not* generate a NAK.
        def invalid(event): raise Exception("Failed")
        self.proto.factory.validators.append(invalid)
        self.proto.stringReceived(DUMMY_VOEVENT)
        received_element = etree.fromstring(self.tr.value()[4:])
        self.assertEqual("ack", received_element.attrib['role'])
        if self.IVOID:
            self.assertEqual(DUMMY_SERVICE_IVOID.decode(),
                             received_element.find('Response').text)
        self.assertEqual(DUMMY_EVENT_IVOID.decode(),
                         received_element.find('Origin').text)

class VOEventSubscriberWithID(VOEventSubscriberTestCase, unittest.TestCase):
    IVOID = DUMMY_SERVICE_IVOID

class VOEventSubscriberWithoutID(VOEventSubscriberTestCase, unittest.TestCase):
    IVOID = None
