# Comet VOEvent Broker.
# Tests for EventWriter plugin.

import os
import shutil

from twisted.trial import unittest
from twisted.plugin import IPlugin

from comet.icomet import IHandler, IHasOptions
from comet.utility import xml_document
from comet.testutils import DUMMY_VOEVENT, temp_dir
from comet.plugins.eventwriter import EventWriter
from comet.plugins.eventwriter import string_to_filename
from comet.plugins.eventwriter import event_file

class StringToFilenameTestCase(unittest.TestCase):
    def test_characters(self):
        test_data = [
            ("abcd", "abcd"),
            ("1234", "1234"),
            ("1a2b", "1a2b"),
            (".abc", "abc"),
            ("a.bc", "a.bc"),
            ("ab/c", "ab_c"),
            ("a*bc", "abc"),
            ("a||b", "ab"),
            ("a\/b", "a__b")
        ]
        for in_str, out_str in test_data:
            self.assertEqual(string_to_filename(in_str), out_str)


class EventFileTestCase(unittest.TestCase):
    def setUp(self):
        self.ivorn = "ivo://test.ivorn/1234#5678"
        with event_file(self.ivorn) as f:
            f.write("Test data")
        self.filename = os.path.join(os.getcwd(), string_to_filename(self.ivorn))

    def tearDown(self):
        os.unlink(self.filename)

    def test_file_created(self):
        self.assertTrue(os.path.exists(self.filename))

    def test_file_contents(self):
        with open(self.filename, 'r') as f:
            self.assertEqual(f.read(), "Test data")

    def test_dup_file(self):
        self.ivorn = "ivo://test.ivorn/1234#5678"
        with event_file(self.ivorn) as f:
            self.assertEqual(f.name, self.filename + ".")

    def test_temp_dir(self):
        with temp_dir() as tmpdir:
            with event_file(self.ivorn, dirname=tmpdir) as f:
                self.assertEqual(os.path.dirname(f.name), tmpdir)


class EventWriterTestCase(unittest.TestCase):
    def setUp(self):
        self.event = xml_document(DUMMY_VOEVENT)
        self.event_writer = EventWriter()

    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventWriter))
        self.assertTrue(IPlugin.implementedBy(EventWriter))
        self.assertTrue(IHasOptions.implementedBy(EventWriter))

    def test_name(self):
        self.assertEqual(EventWriter.name, "save-event")

    def test_save_event(self, root=''):
        self.event_writer(self.event)
        with open(os.path.join(root, string_to_filename(self.event.attrib['ivorn'])), 'r') as f:
            self.assertEqual(f.read(), DUMMY_VOEVENT)

    def test_custom_directory(self):
        self.assertEqual(self.event_writer.get_options()[0][1], os.getcwd())
        with temp_dir() as tmpdir:
            self.event_writer.set_option("directory", tmpdir)
            self.test_save_event(tmpdir)
