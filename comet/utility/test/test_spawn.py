import sys

from twisted.trial import unittest
from twisted.python import failure
from twisted.python import util

from ..spawn import SpawnCommand

class DummyEvent(object):
    def __init__(self, text=None):
        self.text = text

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

    def test_write_data(self):
        TEXT = "Test spawn process"
        def read_data(result):
            f = open("spawnfile.txt")
            try:
                self.assertEqual(f.read(), TEXT)
            finally:
                f.close()
        spawn = SpawnCommand(util.sibpath(__file__, "test_spawn.sh"))
        d = spawn(DummyEvent(TEXT))
        d.addCallback(read_data)
        return d
