# Comet VOEvent Broker.
# Tests for event sender command line options.

import os
from tempfile import TemporaryDirectory

from twisted.trial import unittest

from comet.cmdline import Options
from comet.testutils import DummyEvent, OptionTestUtils


class SenderOptionsTestCase(unittest.TestCase, OptionTestUtils):
    def setUp(self):
        self.config = Options()
        self.tempdir = TemporaryDirectory()
        self.event_filename = os.path.join(self.tempdir.name, "event.xml")
        with open(self.event_filename, "wb") as f:
            f.write(DummyEvent().raw_bytes)

    def tearDown(self):
        # Necessary to enable test cleanup on Win32; otherwise, Windows
        # refuses to remove an open file.
        if "event" in self.config:
            self.config["event"].close()
        self.tempdir.cleanup()

    def test_good_parse(self):
        test_target = "test"
        self.config.parseOptions([test_target, self.event_filename])
        self.assertEqual(self.config["target"], test_target)
        self.assertEqual(self.config["event"].read(), DummyEvent().raw_bytes)

    def test_non_extant_file(self):
        test_target = "test"
        self._check_bad_parse([test_target, self.event_filename + "_"])
