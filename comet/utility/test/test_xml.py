# Comet VOEvent Broker.
# Tests for XML parsing.

import textwrap
import lxml.etree as etree

from twisted.trial import unittest
from comet import BINARY_TYPE
from comet.utility import xml_document, ParseError

EXAMPLE_XML = b"""<xml></xml>"""

class mutable_element_tests(unittest.TestCase):
    def setUp(self):
        self.doc = xml_document(b"<foo>bar</foo>")

    def test_transform_text(self):
        self.assertEqual(self.doc.element.text, "bar")
        self.doc.raw_bytes = b"<foo>baz</foo>"
        self.assertEqual(self.doc.element.text, "baz")

    def test_transform_element(self):
        # Not found in default document
        self.assertEqual(self.doc.raw_bytes.find(b"<foo>baz</foo>"), -1)

        # But is in this replacement
        self.doc.element = etree.fromstring("<foo>baz</foo>")
        self.assertNotEqual(self.doc.raw_bytes.find(b"<foo>baz</foo>"), -1)

class xml_document_encoding(unittest.TestCase):
    def test_from_unicode(self):
        # It should not be possible to initalize an XML document from a
        # unicode string.
        self.assertRaises(ParseError, xml_document, u"<foo>bar</foo>")

    def test_encoding_detection(self):
        # Default case: UTF-8
        doc = xml_document(b"<foo>bar</foo>")
        self.assertEqual(doc.encoding, "UTF-8")

        # Something more exotic!
        doc = xml_document(b"<?xml version=\'1.0\' encoding=\'BIG5\'?><foo>bar</foo>")
        self.assertEqual(doc.encoding, "BIG5")

class xml_document_tests(object):
    def test_signature(self):
        self.assertFalse(self.doc.valid_signature)

    def test_element(self):
        self.assertIsInstance(self.doc.element, etree._Element)

    def test_text(self):
        self.assertIsInstance(self.doc.raw_bytes, BINARY_TYPE)

class xml_document_from_string_TestCase(unittest.TestCase, xml_document_tests):
    def setUp(self):
        self.doc = xml_document(EXAMPLE_XML)

class xml_document_from_element_TestCase(unittest.TestCase, xml_document_tests):
    def setUp(self):
        self.doc = xml_document(etree.fromstring(EXAMPLE_XML))

class xml_security_TestCase(unittest.TestCase):
    """
    Refuse to parse any dangerous XML.

    Since we are accepting XML from the network, we are, in theory, vulnerable
    to a range of exploits: see https://bitbucket.org/tiran/defusedxml for
    details.
    """
    def test_billion_laughs(self):
        """
        Exponential entity expansion.

        http://en.wikipedia.org/wiki/Billion_laughs
        """
        xml_str = textwrap.dedent(u"""
        <?xml version="1.0"?>
        <!DOCTYPE lolz [
         <!ENTITY lol "lol">
         <!ELEMENT lolz (#PCDATA)>
         <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
         <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
         <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
         <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
         <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
         <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
         <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
         <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
         <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
        ]>
        <lolz>&lol9;</lolz>
        """).strip().encode('utf-8')
        self.assertRaises(ParseError, xml_document, xml_str)

    def test_quadratic_blowup(self):
        """
        Quadratic entitty expansion.

        To avoid this, we'll have to disable entity expansion altogether.
        """
        xml_str = textwrap.dedent(u"""
        <?xml version="1.0"?>
        <!DOCTYPE bomb [
        <!ENTITY a "xxxxxxx">
        ]>
        <bomb>&a;&a;&a;&a;&a;</bomb>
        """).strip().encode('utf-8')
        self.assertRaises(ParseError, xml_document, xml_str)
