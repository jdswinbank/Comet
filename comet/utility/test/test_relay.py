from twisted.trial import unittest

from ...icomet import IHandler
from ..relay import EventRelay

DUMMY_EVENT = "Dummy Event Text"

class DummyBroadcaster(object):
    received_event = None
    def send_event(self, event):
        self.received_event = event

class DummyFactory(object):
    broadcasters = [DummyBroadcaster(), DummyBroadcaster()]

class EventRelayTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventRelay))

    def test_name(self):
        self.assertEqual(EventRelay.name, "event-relay")

    def test_send_event(self):
        factory = DummyFactory()
        relay = EventRelay(factory)
        relay(DUMMY_EVENT)
        for broadcaster in factory.broadcasters:
            self.assertEqual(broadcaster.received_event, DUMMY_EVENT)
