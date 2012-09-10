from textwrap import dedent
import lxml.etree as ElementTree

from twisted.trial import unittest
from ..xml import xml_document
from ..xml import dash_escape
from ..xml import dash_unescape
from ...test.support import DUMMY_VOEVENT
from ...test.gpg import GPGTestSupport
from ...test.gpg import GPGTestSupportPublicOnlyKey
from ...test.gpg import GPGTestSupportIndirectKey
from ...test.gpg import GPGTestSupportNonExtantKey
from ...utility import log
from ...utility.exceptions import CometGPGSigFailedException

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


class dash_escape_tests(unittest.TestCase):
    data = [
        (r"^", r"\^"),
        (r"-", r"^"),
        (r"\^", r"\\^"),
        (r"--", r"^^"),
        (r"^^", r"\^\^"),
        (r"^-", r"\^^"),
    ]

    def test_escape(self):
        for pair in self.data:
            self.assertEqual(dash_escape(pair[0]), pair[1])

    def test_unescape(self):
        for pair in self.data:
            self.assertEqual(pair[0], dash_unescape(pair[1]))

    def test_multiline(self):
        pre_escaped = r"""
            -
            ^
            --
            --^--
            ^^
            \^-
        """
        pre_escaped = dedent(pre_escaped)
        escaped = r"""
            ^
            \^
            ^^
            ^^\^^^
            \^\^
            \\^^
        """
        escaped = dedent(escaped)
        self.assertEqual(dash_escape(pre_escaped), escaped)
        self.assertEqual(pre_escaped, dash_unescape(escaped))

    def test_signature(self):
        pre_escaped = r"""
            -----BEGIN PGP SIGNATURE-----
            Version: GnuPG v1.4.12-0^1 (MingW32)

            iF4EABEIAAYFAlAsA5cACgkQiDtWrG4SSODu+QEAp4Mbf8DyB2u45CWqGuGp5WbM
            f547MupOiraPTF5gDi4A/i1OUo9atpHnS3dNAJS14CZ4eNslILqssmvLy2nCu+Yq
            =Ine6
            -----END PGP SIGNATURE-----
        """
        pre_escaped = dedent(pre_escaped)
        escaped = r"""
            ^^^^^BEGIN PGP SIGNATURE^^^^^
            Version: GnuPG v1.4.12^0\^1 (MingW32)

            iF4EABEIAAYFAlAsA5cACgkQiDtWrG4SSODu+QEAp4Mbf8DyB2u45CWqGuGp5WbM
            f547MupOiraPTF5gDi4A/i1OUo9atpHnS3dNAJS14CZ4eNslILqssmvLy2nCu+Yq
            =Ine6
            ^^^^^END PGP SIGNATURE^^^^^
        """
        escaped = dedent(escaped)
        self.assertEqual(dash_escape(pre_escaped), escaped)
        self.assertEqual(pre_escaped, dash_unescape(escaped))


class xml_document_tests(object):
    def test_signature(self):
        self.assertFalse(self.doc.valid_signature())

    def test_element(self):
        self.assertIsInstance(self.doc.element, ElementTree._Element)

    def test_text(self):
        self.assertIsInstance(self.doc.text, str)

class xml_document_from_string_TestCase(GPGTestSupport, xml_document_tests):
    def setUp(self):
        GPGTestSupport.setUp(self)
        self.doc = xml_document(DUMMY_VOEVENT)

class xml_document_from_element_TestCase(GPGTestSupport, xml_document_tests):
    def setUp(self):
        GPGTestSupport.setUp(self)
        self.doc = xml_document(ElementTree.fromstring(DUMMY_VOEVENT))

class test_voevent_signatures(GPGTestSupport):
    def test_signable_text(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signable_text, DUMMY_VOEVENT.replace("\n", "", 1))

    def test_unsigned(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        self.assertEqual(doc.valid_signature(), False)

    def test_untrusted_signature(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc = self._sign_untrusted(doc)
        self.assertNotEqual(doc.signature, None)
        self.assertFalse(doc.valid_signature())

    def test_trusted_signature(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc = self._sign_trusted(doc)
        self.assertNotEqual(doc.signature, None)
        self.assertTrue(doc.valid_signature())

    def test_no_clobber_comments_end(self):
        # We should be able to add, remove and manipulate comments after the
        # end of the VOEvent element without them either being changed by the
        # VOEvent signature or affecting its validity.
        doc = xml_document(DUMMY_VOEVENT + "<!-- a comment -->")
        doc = self._sign_trusted(doc)
        position = doc.text.rfind("a comment")
        self.assertTrue(doc.valid_signature())
        self.assertEqual(position, doc.text.rfind("a comment"))
        doc.text = doc.text.replace("a comment", "another comment")
        self.assertNotEqual(position, doc.text.rfind("a comment"))
        self.assertTrue(doc.valid_signature())

    def test_no_clobber_comments_start(self):
        # We should be able to add, remove and manipulate comments between the
        # XML declaration and the VOEvent element without them either being
        # changed by the VOEvent signature or affecting its validity.
        doc = xml_document(
            DUMMY_VOEVENT.replace(
                "<?xml version=\'1.0\' encoding=\'UTF-8\'?>",
                "<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<!-- a comment -->"
            )
        )
        self.assertEqual(DUMMY_VOEVENT.replace("\n", '', 1), doc.signable_text)
        position = doc.text.find("a comment")
        doc = self._sign_trusted(doc)
        self.assertTrue(doc.valid_signature())
        self.assertEqual(position, doc.text.find("a comment"))
        doc.text = doc.text.replace("a comment", "another comment")
        self.assertNotEqual(position, doc.text.find("a comment"))
        self.assertTrue(doc.valid_signature())

    def test_multisig_mixed(self):
        # If the event is signed twice, once with a trusted signature and once
        # with a trusted signature, we regard it as valid.
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc = self._sign_untrusted(doc)
        doc = self._sign_trusted(doc)
        self.assertNotEqual(doc.signature, None)
        self.assertTrue(doc.valid_signature())

    def test_multisig_bad(self):
        # If the event is signed twice, both times with untrusted signatures,
        # we regard it as invalid.
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc = self._sign_untrusted(doc)
        doc = self._sign_untrusted(doc)
        self.assertNotEqual(doc.signature, None)
        self.assertFalse(doc.valid_signature())

class NonExistentKey(GPGTestSupportNonExtantKey):
    def test_make_sig_fails(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertRaises(CometGPGSigFailedException, self._sign_untrusted, doc)

class PublicOnlyKey(GPGTestSupportPublicOnlyKey):
    def test_make_sig_fails(self):
        doc = xml_document(DUMMY_VOEVENT)
        self.assertRaises(CometGPGSigFailedException, self._sign_untrusted, doc)

class IndirectKey(GPGTestSupportIndirectKey):
    def test_countersignature_trust(self):
        # Even if the signing key is trusted, we reject the signature from a
        # key with a bad user ID unless it is countersigned by a key with a
        # good user ID.
        doc = xml_document(DUMMY_VOEVENT)
        self.assertEqual(doc.signature, None)
        doc = self._sign_trusted(doc)
        self.assertNotEqual(doc.signature, None)
        self.assertFalse(doc.valid_signature())
        self._sign_indirect_key()
        self.assertTrue(doc.valid_signature())
