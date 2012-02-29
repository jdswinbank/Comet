from twisted.trial import unittest
from twisted.test import proto_helpers

from ..protocol import VOEventSubscriber
from ..protocol import VOEventSubscriberFactory

DUMMY_IVORN = "ivo://comet.broker/test#1234567890"

class VOEventSubscriberFactoryTestCase(unittest.TestCase):
    def setUp(self):
        factory = VOEventSubscriberFactory(DUMMY_IVORN)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.makeConnection(proto_helpers.StringTransport())

    def test_protocol(self):
        self.assertIsInstance(self.proto, VOEventSubscriber)

    def tearDown(self):
        self.proto.connectionLost()
