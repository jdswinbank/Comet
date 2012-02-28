import os
import sys

from twisted.python import log
from twisted.trial import unittest
from twisted.python import failure
from twisted.python import util

from ..ivorn_db import IVORN_DB
from ..ivorn_db import CheckPreviouslySeen

DUMMY_IVORN = "ivo://comet.broker/test#1234567890"

class DummyEvent(object):
    attrib = {'ivorn': DUMMY_IVORN}

class IVORN_DB_TestCase(unittest.TestCase):
    def setUp(self):
        self.ivorn_db = IVORN_DB('.')

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
        for database in self.ivorn_db.databases.iterkeys():
            os.unlink(database)

class CheckPreviouslySeenTestCase(unittest.TestCase):
    def setUp(self):
        self.checker = CheckPreviouslySeen(IVORN_DB('.'))
        self.event = DummyEvent()

    def test_unseen(self):
        d = self.checker(self.event)
        d.addCallback(self.assertTrue)
        return d

    def test_seen(self):
        self.checker.ivorn_db.check_ivorn(self.event.attrib['ivorn'])
        d = self.checker(self.event)
        d.addErrback(self.assertIsInstance, failure.Failure)
        return d

    def tearDown(self):
        for database in self.checker.ivorn_db.databases.iterkeys():
            os.unlink(database)

