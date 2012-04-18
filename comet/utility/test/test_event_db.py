import os
import tempfile
import shutil

from twisted.trial import unittest
from twisted.python import failure

from ...test.support import DummyEvent

from ...icomet import IValidator
from ..event_db import Event_DB
from ..event_db import CheckPreviouslySeen

class Event_DB_TestCase(unittest.TestCase):
    def setUp(self):
        self.event_db_dir = tempfile.mkdtemp()
        self.event_db = Event_DB(self.event_db_dir)
        self.event = DummyEvent()

    def test_unseen(self):
        # First time through, we've not seen this event so this should be True.
        self.assertTrue(self.event_db.check_event(self.event))

    def test_seen(self):
        # Second time through, we have seen the event, so it should be False.
        self.event_db.check_event(self.event)
        self.assertFalse(self.event_db.check_event(self.event))

    def test_prune(self):
        def done_prune(result):
            self.assertTrue(self.event_db.check_event(self.event))
        self.event_db.check_event(self.event)
        d = self.event_db.prune(0)
        d.addCallback(done_prune)
        return d

    def tearDown(self):
        shutil.rmtree(self.event_db_dir)

class CheckPreviouslySeenTestCase(unittest.TestCase):
    def setUp(self):
        self.event_db_dir = tempfile.mkdtemp()
        self.checker = CheckPreviouslySeen(Event_DB(self.event_db_dir))
        self.event = DummyEvent()

    def test_unseen(self):
        d = self.checker(self.event)
        d.addCallback(self.assertTrue)
        return d

    def test_seen(self):
        self.checker.event_db.check_event(self.event)
        return self.assertFailure(self.checker(self.event), Exception)

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.checker))

    def tearDown(self):
        shutil.rmtree(self.event_db_dir)
