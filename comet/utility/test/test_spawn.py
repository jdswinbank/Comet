import sys

from twisted.trial import unittest
from twisted.python import failure

from ..spawn import SpawnCommand

class DummyEvent(object):
    text = ""

class SpawnCommandProtocolTestCase(unittest.TestCase):
    def test_good_process(self):
        spawn = SpawnCommand(sys.executable)
        d = spawn(DummyEvent())
        d.addCallback(self.assertEqual, True)
        return d

    def test_bad_process(self):
        spawn = SpawnCommand("/not/a/real/executable")
        d = spawn(DummyEvent())
        d.addErrback(self.assertIsInstance, failure.Failure)
        return d
