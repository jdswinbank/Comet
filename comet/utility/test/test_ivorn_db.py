import os
import tempfile
import shutil

from twisted.trial import unittest
from twisted.python import failure

from ...test.support import DUMMY_EVENT_IVORN as DUMMY_IVORN
from ...test.support import DummyEvent

from ...icomet import IValidator
from ..ivorn_db import IVORN_DB
from ..ivorn_db import CheckPreviouslySeen

class IVORN_DB_TestCase(unittest.TestCase):
    def setUp(self):
        self.ivorn_db_dir = tempfile.mkdtemp()
        self.ivorn_db = IVORN_DB(self.ivorn_db_dir)

    def test_unseen(self):
        # First time through, we've not seen this IVORN so this should be True.
        self.assertTrue(self.ivorn_db.check_ivorn(DUMMY_IVORN))

    def test_seen(self):
        # Second time through, we have seen the IVORN, so it should be False.
        self.ivorn_db.check_ivorn(DUMMY_IVORN)
        self.assertFalse(self.ivorn_db.check_ivorn(DUMMY_IVORN))

    def test_prune(self):
        def done_prune(result):
            self.assertTrue(self.ivorn_db.check_ivorn(DUMMY_IVORN))
        self.ivorn_db.check_ivorn(DUMMY_IVORN)
        d = self.ivorn_db.prune(0)
        d.addCallback(done_prune)
        return d

    def tearDown(self):
        shutil.rmtree(self.ivorn_db_dir)

class CheckPreviouslySeenTestCase(unittest.TestCase):
    def setUp(self):
        self.ivorn_db_dir = tempfile.mkdtemp()
        self.checker = CheckPreviouslySeen(IVORN_DB(self.ivorn_db_dir))
        self.event = DummyEvent()

    def test_unseen(self):
        d = self.checker(self.event)
        d.addCallback(self.assertTrue)
        return d

    def test_seen(self):
        self.checker.ivorn_db.check_ivorn(self.event.attrib['ivorn'])
        return self.assertFailure(self.checker(self.event), Exception)

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.checker))

    def tearDown(self):
        shutil.rmtree(self.ivorn_db_dir)

