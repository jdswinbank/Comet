# Comet VOEvent Broker.
# Tests for VOEvent messaage handling.

import os
import string
import lxml.etree as etree

from twisted.trial import unittest

import comet
from comet.utility import broker_test_message
from comet.utility import parse_ivorn
from comet.testutils import DUMMY_SERVICE_IVORN

class broker_test_messageTestCase(unittest.TestCase):
    def setUp(self):
        self.message = broker_test_message(DUMMY_SERVICE_IVORN)

    def test_valid(self):
        schema = etree.XMLSchema(
            etree.parse(
                os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
            )
        )
        self.assertTrue(schema.validate(self.message.element))

class parse_ivornTestCase(unittest.TestCase):
    # Character classes as defined by the IVOA Identifiers spec, 1.12
    ALPHANUM = string.ascii_letters + string.digits
    MARK = "-_."
    DISCOURAGED = "~*'()"
    UNRESERVED = ALPHANUM + MARK + DISCOURAGED
    RESERVED = "?;:@!&$,"
    DISALLOWED = "<>#%\"`?{}|\\^[]+="

    def _build_ivorn(self, auth, rsrc, local):
        return "ivo://%s/%s#%s" % (auth, rsrc, local)

    def _bad_parse(self, auth, rsrc, local):
        # IVORN parsing should fail: parse_ivorn() raises.
        ivorn = self._build_ivorn(auth, rsrc, local)
        self.assertRaises(Exception, parse_ivorn, ivorn)

    def _good_parse(self, auth, rsrc, local):
        # IVORN should be parsed and inputs recovered.
        ivorn = self._build_ivorn(auth, rsrc, local)
        self.assertEqual(parse_ivorn(ivorn), (auth, rsrc, local))

    def test_simple(self):
        for auth, rsrc, local in [
            ("authorityID", "resourceKey", "local_ID"),
            ("authorityID", "rsrc/with/slashes", "local/ID/with/slashes"),
            ("authorityID", "resourceKey", ""),
            ("authorityID", "", "local_ID"),
            ("authorityID", "", "")
        ]:
            self._good_parse(auth, rsrc, local)

    def test_no_fragment(self):
        auth, rsrc = "authorityID", "resourceKey"
        ivorn = "ivo://%s/%s" % (auth, rsrc)
        self.assertEqual((auth, rsrc, ''), parse_ivorn(ivorn))

    def test_partial_ivorn(self):
        for ivorn in [
            "ivo://#localID",
            "ivo:///resourceKey#",
            "ivo://"
        ]:
            self.assertRaises(Exception, parse_ivorn, ivorn)

    def test_authority_id(self):
        # Per IVOA Identifiers spec:
        #
        #   AUTHORITYID = ALPHANUM 2*UNRESERVED

        # Authority ID must contain at least three characters
        self._bad_parse("au", "rsrc", "local")

        # Authority ID must start with an alphanumeric
        self._bad_parse("_auth", "rsrc", "local")
        self._good_parse("1auth", "rsrc", "local")

        # Authority ID may contain any unreserved character
        for char in self.UNRESERVED:
            self._good_parse("auth" + char, "rsrc", "local")

        # Authority ID may not contain any reserved or disallowed character
        for char in self.RESERVED + self.DISALLOWED:
            self._bad_parse("auth" + char, "rsrc", "local")
            self._bad_parse(char + "auth", "rsrc", "local")

    def test_resource_key(self):
        # Per IVOA identifiers spec:
        #
        #   RESOURCEKEY = SEGMENT *( "/" SEGMENT)
        #   SEGMENT     = *UNRESERVED
        self._good_parse("auth", "rsrc", "local")
        self._good_parse("auth", "rsrc/", "local")
        self._good_parse("auth", "rsrc/rsrc", "local")
        self._good_parse("auth", "rs", "local")
        self._good_parse("auth", "_rsrc", "local")
        self._good_parse("auth", "1rsrc", "local")

        for char in self.UNRESERVED:
            self._good_parse("auth", "rsrc" + char, "local")
            self._good_parse("auth", char + "rsrc", "local")

        for char in self.RESERVED + self.DISALLOWED:
            self._bad_parse("auth", "rsrc" + char, "local")
            self._bad_parse("auth", char + "rsrc", "local")

    def test_fragment(self):
        # The IVOA spec (\S3.2.2) asserts that the fragment identifier ("#") is a
        # "stop" character. and excludes everything subsequent to the fragment
        # from processing as an identifier.
        # We interpret that as meaning that all characters valid for use in a
        # URL may appear in the fragment without further reference to IVOA
        # standards, and refer to RFC-3986. This defines:
        #
        # FRAGMENT    = *( pchar / "/" / "?" )
        # PCHAR       = UNRESERVED / PCT-ENCODED / SUB-DELIMS / ":" / "@"
        # SUB-DELIMS  = "!" / "$" / "&" / "'" / "(" / ")"
        #             / "*" / "+" / "," / ";" / "="
        # UNRESERVED  = ALPHA / DIGIT / "-" / "." / "_" / "~"
        # PCT_ENCODED = "%" HEXDIG HEXDIG

        ALLOWED = self.ALPHANUM + "-._~%!$&'()*+,;=:@/?"
        FORBIDDEN = "#[]"

        for char in ALLOWED:
            self._good_parse("auth", "rsrc", "local" + char)
            self._good_parse("auth", "rsrc", char + "local")

        for char in FORBIDDEN:
            self._bad_parse("auth", "rsrc", "local" + char)
            self._bad_parse("auth", "rsrc", char + "local")
