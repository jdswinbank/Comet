# Comet VOEvent Broker.
# Event database tests.

import os
import shutil
import stat
import tempfile
import time
from functools import reduce
from itertools import repeat, permutations
from multiprocessing.pool import ThreadPool
from operator import __or__

from twisted.trial import unittest

from comet.testutils import DummyEvent
from comet.utility.event_db import Event_DB

class Event_DB_TestCase(unittest.TestCase):
    def setUp(self):
        self.event_db_dir = tempfile.mkdtemp()
        self.event_db = Event_DB(self.event_db_dir)
        self.event = DummyEvent()

    def test_non_existing_dir(self):
        # If the root for the Event_DB doesn't exist, we should create it.
        # Note the relative path means that this DB will be created in the
        # _trial_temp directory.
        event_db = Event_DB("event_db_test_%.5f" % (time.time(),))
        self.assertTrue(event_db.check_event(self.event))

    def test_dir_is_file(self):
        # If the path specified for the Event_DB *does* exist but isn't a
        # directory, then we should fail fast.
        filename = "event_db_test_%.5f" % (time.time(),)
        open(filename, 'w').close()
        self.assertRaises(RuntimeError, Event_DB, filename)

    def test_dir_is_unusable(self):
        # If the path specified for the Event_DB exists and is a directory,
        # but we don't have permissions to use it, fail fast.
        filename = "event_db_test_%.5f" % (time.time(),)
        os.makedirs(filename)
        os.chmod(filename, 0)
        self.assertRaises(RuntimeError, Event_DB, filename)
        for n_perms in [1, 2]:
            for perms in permutations([stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR],
                                      n_perms):
                os.chmod(filename, reduce(__or__, perms))
                self.assertRaises(RuntimeError, Event_DB, filename)
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        self.assertTrue(Event_DB(filename).check_event(self.event))

    def test_unseen(self):
        # Unseen event -> return True
        self.assertTrue(self.event_db.check_event(self.event))

    def test_seen(self):
        # Seen event -> return False
        self.event_db.check_event(self.event)
        self.assertFalse(self.event_db.check_event(self.event))

    def test_threadsafe(self):
        # Ensure that the eventdb is thread-safe by hammering on it with
        # multiple threads simultaneously. We should only get one positive.
        pool = ThreadPool(10)
        results = pool.map(self.event_db.check_event, repeat(self.event, 1000))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 999)

    def test_prune(self):
        def done_prune(result):
            self.assertTrue(self.event_db.check_event(self.event))
        self.event_db.check_event(self.event)
        d = self.event_db.prune(0)
        d.addCallback(done_prune)
        return d

    def test_bad_ivoid(self):
        bad_event = DummyEvent(b"ivo://#")
        self.assertFalse(self.event_db.check_event(bad_event))

    def test_prune_bad_event(self):
        bad_event = DummyEvent(ivoid=b"ivo://")
        self.assertNotIn("", self.event_db.databases)
        # This event doesn't validate and is rejected.
        self.assertFalse(self.event_db.check_event(bad_event))
        # The hostname shouldn't event be stored in our list of databases.
        self.assertNotIn("", self.event_db.databases)
        d = self.event_db.prune(0)

        def done_prune(result):
            # After pruning, everything in the database should be unlocked.
            for lock in self.event_db.databases.values():
                self.assertFalse(lock.locked())
            self.assertFalse(self.event_db.check_event(bad_event))
            self.assertTrue(self.event_db.check_event(self.event))
        d.addCallback(done_prune)
        return d

    def tearDown(self):
        shutil.rmtree(self.event_db_dir)
