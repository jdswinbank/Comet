import tempfile
import shutil

from twisted.trial import unittest

from ...test.support import DummyEvent
from ..event_db import Event_DB

class Event_DB_TestCase(unittest.TestCase):
    def setUp(self):
        self.event_db_dir = tempfile.mkdtemp()
        self.event_db = Event_DB(self.event_db_dir)
        self.event = DummyEvent()

    def test_unseen(self):
        # Unseen event -> return True
        self.assertTrue(self.event_db.check_event(self.event))

    def test_seen(self):
        # Seen event -> return False
        self.event_db.record_event(self.event)
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