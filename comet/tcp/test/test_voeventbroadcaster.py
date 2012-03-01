from twisted.internet import reactor
from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_EVENT_IVORN as DUMMY_IVORN

from ..protocol import VOEventBroadcaster
from ..protocol import VOEventBroadcasterFactory

class DummyBroadcaster(object):
    def __init__(self):
        received_alive = False
        received_event = False

    def sendIAmAlive(self):
        self.received_alive = True

    def send_event(self, event):
        self.received_event = True

class VOEventBroadcasterFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = VOEventBroadcasterFactory(DUMMY_IVORN)
        self.factory.alive_loop.clock = task.Clock()
        self.factory.test_loop.clock = task.Clock()
        self.factory.broadcasters.append(DummyBroadcaster())
        self.connector = reactor.listenTCP(0, self.factory)

    def tearDown(self):
        return self.connector.stopListening()

    def test_protocol(self):
        self.assertEqual(self.factory.protocol, VOEventBroadcaster)

    def test_sendIamAlive(self):
        self.assertEqual(self.factory.alive_loop.running, True)
        self.factory.alive_loop.clock.advance(self.factory.IAMALIVE_INTERVAL)
        for broadcaster in self.factory.broadcasters:
            self.assertEqual(broadcaster.received_alive, True)

    def test_sendTestEvent(self):
        self.assertEqual(self.factory.test_loop.running, True)
        self.factory.alive_loop.clock.advance(self.factory.TEST_INTERVAL)
        for broadcaster in self.factory.broadcasters:
            self.assertEqual(broadcaster.received_event, True)
