import os
import sys
import shutil
import tempfile

from twisted.trial import unittest
from twisted.plugin import IPlugin

from ...utility.xml import xml_document
from ...icomet import IHandler, IHasOptions
from ...test.support import DUMMY_VOEVENT
from ..eventwriter import EventWriter
from ..eventwriter import string_to_filename
from ..eventwriter import event_file

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
        tmpdir = tempfile.mkdtemp()
        with event_file(self.ivorn, dirname=tmpdir) as f:
            self.assertEqual(os.path.dirname(f.name), tmpdir)
        shutil.rmtree(tmpdir)

class EventWriterTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventWriter))
        self.assertTrue(IPlugin.implementedBy(EventWriter))
        self.assertTrue(IHasOptions.implementedBy(EventWriter))

    def test_name(self):
        self.assertEqual(EventWriter.name, "save-event")

    def test_save_event(self):
        event = xml_document(DUMMY_VOEVENT)
        event_writer = EventWriter()
        event_writer(event)
        with open(string_to_filename(event.attrib['ivorn']), 'r') as f:
            self.assertEqual(f.read(), DUMMY_VOEVENT)
