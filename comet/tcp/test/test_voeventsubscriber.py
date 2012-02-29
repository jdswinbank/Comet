from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_EVENT_IVORN as DUMMY_IVORN

from ..protocol import VOEventSubscriber
from ..protocol import VOEventSubscriberFactory

class VOEventSubscriberFactoryTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.makeConnection(proto_helpers.StringTransport())

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSubscriber)

    def tearDown(self):
        self.proto.connectionLost()

class VOEventSubscriberTimeoutTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_timeout(self):
        self.clock.advance(self.proto.ALIVE_INTERVAL)
        self.assertEqual(self.tr.disconnecting, True)
