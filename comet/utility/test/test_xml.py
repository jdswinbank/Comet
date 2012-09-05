import lxml.etree as ElementTree

from twisted.trial import unittest
from comet.utility.xml import xml_document

EXAMPLE_XML = """<xml></xml>"""

class mutable_element_tests(unittest.TestCase):
    def setUp(self):
        self.doc = xml_document("<foo>bar</foo>")

    def test_transform_text(self):
        self.assertEqual(self.doc.element.text, "bar")
        self.doc.text = "<foo>baz</foo>"
        self.assertEqual(self.doc.element.text, "baz")

    def test_transform_element(self):
        self.assertEqual(self.doc.text.find("<foo>baz</foo>"), -1)
        self.doc.element = ElementTree.fromstring("<foo>baz</foo>")
        self.assertNotEqual(self.doc.text.find("<foo>baz</foo>"), -1)


class xml_document_tests(object):
    def test_signature(self):
        self.assertFalse(self.doc.valid_signature)

    def test_element(self):
        self.assertIsInstance(self.doc.element, ElementTree._Element)

    def test_text(self):
        self.assertIsInstance(self.doc.text, str)

class xml_document_from_string_TestCase(unittest.TestCase, xml_document_tests):
    def setUp(self):
        self.doc = xml_document(EXAMPLE_XML)

class xml_document_from_element_TestCase(unittest.TestCase, xml_document_tests):
    def setUp(self):
        self.doc = xml_document(ElementTree.fromstring(EXAMPLE_XML))
