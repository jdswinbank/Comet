# Comet VOEvent Broker.
# Tests for identifying prevously unseen events.

import tempfile
import shutil

from twisted.trial import unittest

from comet.testutils import DummyEvent

from comet.icomet import IValidator
from comet.utility import Event_DB
from comet.validator import CheckPreviouslySeen

class CheckPreviouslySeenTestCase(unittest.TestCase):
    def setUp(self):
        self.event_db_dir = tempfile.mkdtemp()
        self.checker = CheckPreviouslySeen(Event_DB(self.event_db_dir))
        self.event = DummyEvent()

    def test_unseen(self):
        d = self.checker(self.event)
        d.addCallback(self.assertTrue)
        return d

    def test_previously_checked(self):
        self.checker.event_db.check_event(self.event)
        return self.assertFailure(self.checker(self.event), Exception)

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.checker))

    def tearDown(self):
        shutil.rmtree(self.event_db_dir)
