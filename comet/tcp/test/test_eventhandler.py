import lxml.etree as etree

from twisted.trial import unittest
from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.internet.protocol import ServerFactory

from ...test.support import DUMMY_EVENT_IVORN as DUMMY_IVORN
from ...test.support import DummyEvent

from ..protocol import EventHandler

class EventHandlerFactory(ServerFactory):
    protocol = EventHandler
    local_ivo = DUMMY_IVORN

class Succeeds(object):
    has_run = False
    def __call__(self, event):
        self.has_run = True
        return self.has_run

class Fails(object):
    has_run = False
    def __call__(self, event):
        self.has_run = True
        raise Exception(self.has_run)

class EventHandlerTestCase(unittest.TestCase):
    def setUp(self):
        factory = EventHandlerFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_validate_event_valid(self):
        self.proto.factory.validators = [Succeeds()]
        d = self.proto.validate_event(True)
        d.addCallback(self.assertEqual, [True])
        return d

    def test_validate_event_invalid(self):
        self.proto.factory.validators = [Fails()]
        return self.assertFailure(self.proto.validate_event(True), defer.FirstError)

    def test_handle_event_succeeds(self):
        self.proto.factory.handlers = [Succeeds()]
        d = self.proto.handle_event(True)
        d.addCallback(self.assertEqual, [True])
        return d

    def test_handle_event_fails(self):
        self.proto.factory.handlers = [Fails()]
        return self.assertFailure(self.proto.handle_event(True), defer.FirstError)

    def _check_for_role(self, result, role):
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            role
        )

    def _check_for_handler_runs(self, result, should_run):
        for handler in self.proto.factory.handlers:
            self.assertEqual(handler.has_run, should_run)

    def test_process_event_valid_succeeds(self):
        self.proto.factory.validators = [Succeeds()]
        self.proto.factory.handlers = [Succeeds()]
        d = self.proto.process_event(DummyEvent())
        d.addCallback(self._check_for_role, "ack")
        d.addCallback(self._check_for_handler_runs, True)
        return d

    def test_process_event_valid_fails(self):
        self.proto.factory.validators = [Succeeds()]
        self.proto.factory.handlers = [Fails()]
        d = self.proto.process_event(DummyEvent())
        d.addCallback(self._check_for_role, "ack")
        d.addCallback(self._check_for_handler_runs, True)
        return d

    def test_process_event_invalid_can_nak(self):
        self.proto.factory.validators = [Fails()]
        self.proto.factory.handlers = [Succeeds()]
        d = self.proto.process_event(DummyEvent())
        d.addCallback(self._check_for_role, "nak")
        d.addCallback(self._check_for_handler_runs, False)
        return d

    def test_process_event_invalid_cant_nak(self):
        self.proto.factory.validators = [Fails()]
        self.proto.factory.handlers = [Succeeds()]
        d = self.proto.process_event(DummyEvent(), can_nak=False)
        d.addCallback(self._check_for_role, "ack")
        d.addCallback(self._check_for_handler_runs, False)
        return d
