import os
import sys
import tempfile
from unittest import skipUnless

from twisted.trial import unittest
from twisted.python import util
from twisted.python import log as twisted_log

import comet.log as log
from comet.icomet import IHandler
from comet.handler import SpawnCommand
from comet.testutils import DummyEvent, DummyLogObserver

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

    def test_no_exec(self):
        """
        Fail when the executable doesn't exist.
        """
        spawn = SpawnCommand("/not/a/real/executable")
        return self.assertFailure(spawn(DummyEvent()), Exception)

    def _check_logged_value(self, script_name, sentinel, should_fail=False):
        observer = DummyLogObserver()
        twisted_log.addObserver(observer)
        log.LEVEL = log.Levels.DEBUG
        spawn = SpawnCommand(SHELL, util.sibpath(__file__, script_name))
        def _check_log(_):
            self.assertTrue(sentinel in
                            " ".join(msg[0] for msg in observer.messages))
        d = spawn(DummyEvent())
        if should_fail:
            return self.assertFailure(d, Exception).addCallback(_check_log)
        else:
            d.addCallback(_check_log)
            return d

    @skipUnless(os.access(SHELL, os.X_OK), "Shell executable not available")
    def test_bad_process(self):
        """
        Fail when the executable returns non-zero
        """
        # Script returns a 99; we should be able to read that in the logs.
        return self._check_logged_value("test_spawn_failure.sh", "99", True)

    @skipUnless(os.access(SHELL, os.X_OK), "Shell executable not available")
    def test_stdout(self):
        """
        Demonstrate we can read stdout from the process.
        """
        # Script prints the string THIS_IS_STDOUT; we should be able to read
        # that in the logs.
        return self._check_logged_value("test_spawn_stdout.sh", "THIS_IS_STDOUT")

    @skipUnless(os.access(SHELL, os.X_OK), "Shell executable not available")
    def test_stderr(self):
        """
        Demonstrate we can read stderr from the process.
        """
        # Script prints the string THIS_IS_STDERR to standard error; we should
        # be able to read that in the logs.
        return self._check_logged_value("test_spawn_stdout.sh", "THIS_IS_STDERR")

    @skipUnless(os.access(SHELL, os.X_OK), "Shell executable not available")
    def test_write_data(self):
        """
        Demonstrate that an external command can save data.
        """
        output_file = tempfile.NamedTemporaryFile()
        dummy_event = DummyEvent()
        def read_data(result):
            try:
                # NamedTemporaryFile is opened in binary mode, so we compare
                # raw bytes.
                self.assertEqual(output_file.read(), dummy_event.raw_bytes)
            finally:
                output_file.close()
        spawn = SpawnCommand(SHELL, util.sibpath(__file__, "test_spawn_output.sh"), output_file.name)
        d = spawn(dummy_event)
        d.addCallback(read_data)
        return d
