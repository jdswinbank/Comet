import os
import sys
import tempfile

from twisted.trial import unittest
from twisted.python import failure
from twisted.python import util

from ...icomet import IHandler
from ..spawn import SpawnCommand

SHELL = '/bin/sh'

class DummyEvent(object):
    def __init__(self, text=None):
        self.text = text

class SpawnCommandProtocolTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(SpawnCommand))

    def test_good_process(self):
        spawn = SpawnCommand(sys.executable)
        d = spawn(DummyEvent())
        d.addCallback(self.assertEqual, True)
        return d

    def test_bad_process(self):
        spawn = SpawnCommand("/not/a/real/executable")
        return self.assertFailure(spawn(DummyEvent()), Exception)

    def test_write_data(self):
        if not os.access(SHELL, os.X_OK):
            raise unittest.SkipTest("Shell not available")
        TEXT = "Test spawn process"
        output_file = tempfile.NamedTemporaryFile()
        def read_data(result):
            try:
                self.assertEqual(output_file.read(), TEXT)
            finally:
                output_file.close()
        spawn = SpawnCommand('/bin/sh', util.sibpath(__file__, "test_spawn.sh"), output_file.name)
        d = spawn(DummyEvent(TEXT))
        d.addCallback(read_data)
        return d
