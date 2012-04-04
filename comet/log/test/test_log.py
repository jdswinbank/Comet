from twisted.trial import unittest
from twisted.python import log as twisted_log
from twisted.internet import defer

import comet.log.log as log

DUMMY_MESSAGE = "Dummy message"

class DummyLogObserver(object):
    def __init__(self):
        self.messages = []

    def __call__(self, logentry):
        self.messages.append(logentry['message'])

class test_comet_logging(unittest.TestCase):
    def setUp(self):
        self.observer = DummyLogObserver()
        twisted_log.addObserver(self.observer)

    def tearDown(self):
        twisted_log.removeObserver(self.observer)

    def _check_log_full(self, cb):
        self.assertTrue(self.observer.messages)

    def _check_log_empty(self, cb):
        self.assertFalse(self.observer.messages)

    def test_log_debug_level_debug(self):
        log.LEVEL = log.Levels.DEBUG
        self.assertFalse(self.observer.messages)
        d = log.debug(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_full)

    def test_log_debug_level_info(self):
        log.LEVEL = log.Levels.INFO
        self.assertFalse(self.observer.messages)
        d = log.debug(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_empty)

    def test_log_debug_level_warning(self):
        log.LEVEL = log.Levels.WARNING
        self.assertFalse(self.observer.messages)
        d = log.debug(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_empty)

    def test_log_info_level_debug(self):
        log.LEVEL = log.Levels.DEBUG
        self.assertFalse(self.observer.messages)
        d = log.info(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_full)

    def test_log_info_level_info(self):
        log.LEVEL = log.Levels.INFO
        self.assertFalse(self.observer.messages)
        d = log.info(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_full)

    def test_log_info_level_warning(self):
        log.LEVEL = log.Levels.WARNING
        self.assertFalse(self.observer.messages)
        d = log.info(DUMMY_MESSAGE)
        self.assertIsInstance(d, defer.Deferred)
        return d.addCallback(self._check_log_empty)

    def test_log_warning_level_debug(self):
        log.LEVEL = log.Levels.DEBUG
        self.assertFalse(self.observer.messages)
        d = log.warning(DUMMY_MESSAGE)
        self.assertTrue(self.observer.messages)
        return d.addCallback(self._check_log_full)

    def test_log_warning_level_info(self):
        log.LEVEL = log.Levels.INFO
        self.assertFalse(self.observer.messages)
        d = log.warning(DUMMY_MESSAGE)
        self.assertTrue(self.observer.messages)
        return d.addCallback(self._check_log_full)

    def test_log_warning_level_warning(self):
        log.LEVEL = log.Levels.WARNING
        self.assertFalse(self.observer.messages)
        d =log.warning(DUMMY_MESSAGE)
        self.assertTrue(self.observer.messages)
        return d.addCallback(self._check_log_full)

    def test_default_level(self):
        self.assertEqual(log.DEFAULT_LEVEL, log.Levels.INFO)
