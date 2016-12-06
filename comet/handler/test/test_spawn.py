import os
import sys
import tempfile
from unittest import skipUnless

from twisted.trial import unittest
from twisted.python import util

from comet.icomet import IHandler
from comet.handler import SpawnCommand
from comet.testutils import DummyEvent

# Used for spawning test code.
SHELL = '/bin/sh'

# This executable is required to exist and to exit cleanly regardless of
# whatever we squirt into its stdin. Other than that, it doesn't matter what
# it does.
EXECUTABLE = '/bin/ls'

class SpawnCommandProtocolTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(SpawnCommand))

    @skipUnless(os.access(EXECUTABLE, os.X_OK), "Test executable not available")
    def test_good_process(self):
        spawn = SpawnCommand(EXECUTABLE)
        d = spawn(DummyEvent())
        d.addCallback(self.assertEqual, True)
        return d

    def test_bad_process(self):
        spawn = SpawnCommand("/not/a/real/executable")
        return self.assertFailure(spawn(DummyEvent()), Exception)

    @skipUnless(os.access(SHELL, os.X_OK), "Shell executable not available")
    def test_write_data(self):
        output_file = tempfile.NamedTemporaryFile()
        dummy_event = DummyEvent()
        def read_data(result):
            try:
                # NamedTemporaryFile is opened in binary mode, so we compare
                # raw bytes.
                self.assertEqual(output_file.read(), dummy_event.raw_bytes)
            finally:
                output_file.close()
        spawn = SpawnCommand(SHELL, util.sibpath(__file__, "test_spawn.sh"), output_file.name)
        d = spawn(dummy_event)
        d.addCallback(read_data)
        return d
