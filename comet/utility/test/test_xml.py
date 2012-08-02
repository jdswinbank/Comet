import os
import tempfile
import shutil
import gpgme
import gpgme.editutil
import lxml.etree as ElementTree

from twisted.trial import unittest
from comet.utility.xml import xml_document
from comet.test.support import DUMMY_VOEVENT

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
        self.assertFalse(self.doc.valid_signature())

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

class test_voevent_signatures(unittest.TestCase):
    PASSPHRASE = "comet"
    KEY_ID = "71837D03"

    def setUp(self):
        self._gpghome = tempfile.mkdtemp(prefix="tmp.gpghome")
        os.environ["GNUPGHOME"] = self._gpghome
        ctx = gpgme.Context()
        with open(os.path.join(os.path.dirname(__file__), "comet.secret.asc"), 'r') as k_fp:
            ctx.import_(k_fp)

    def tearDown(self):
        del os.environ["GNUPGHOME"]
        shutil.rmtree(self._gpghome, ignore_errors=True)

    def test_unsigned(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        self.assertEqual(doc.valid_signature(), False)

    def test_untrusted_signature(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc.sign(self.PASSPHRASE, self.KEY_ID)
        self.assertNotEqual(doc.signature, None)
        self.assertEqual(doc.valid_signature(), False)

    def test_trusted_signature(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc.sign(self.PASSPHRASE, self.KEY_ID)
        self.assertNotEqual(doc.signature, None)
        self.assertEqual(doc.valid_signature(), False)
        ctx = gpgme.Context()
        gpgme.editutil.edit_trust(ctx, ctx.get_key(self.KEY_ID, True), gpgme.VALIDITY_ULTIMATE)
        self.assertEqual(doc.valid_signature(), True)
