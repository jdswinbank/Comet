import os
import sys
import shutil
import tempfile
#from cStringIO import StringIO

#import lxml.etree as etree

from twisted.trial import unittest
#from twisted.plugin import IPlugin

#from ...icomet import IHandler
#from ..eventwriter import EventWriter
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
