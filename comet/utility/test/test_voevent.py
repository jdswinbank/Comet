import os
import lxml.etree as etree

from twisted.trial import unittest

from ...test.support import DUMMY_SERVICE_IVORN as DUMMY_IVORN

import comet
from ..voevent import broker_test_message
from ..voevent import parse_ivorn

class broker_test_messageTestCase(unittest.TestCase):
    def setUp(self):
        self.message = broker_test_message(DUMMY_IVORN)

    def test_valid(self):
        schema = etree.XMLSchema(
            etree.parse(
                os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
            )
        )
        self.assertTrue(schema.validate(self.message.element))

class parse_ivornTestCase(unittest.TestCase):
    def test_simple(self):
        for auth, rsrc, local_ID in [
            ("authorityID", "resourceKey", "local_ID"),
            ("authorityID", "rsrc/with/slashes", "local/ID/with/slashes"),
            ("authorityID", "resourceKey", ""),
            ("authorityID", "", "local_ID"),
            ("authorityID", "", "")
        ]:
            ivorn = "ivo://%s/%s#%s" % (auth, rsrc, local_ID)
            self.assertEqual((auth, rsrc, local_ID), parse_ivorn(ivorn))

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

    def test_reserved_chars(self):
        # These are forbidden by the IVOA Identifiers Version 1.12 spec
        reserved = ["?", ";", ":", "@", "!", "&", "$", ","]
        for char in reserved:
            self.assertRaises(Exception, parse_ivorn, "ivo://%s/rsrc#local" % (char, ))
            self.assertRaises(Exception, parse_ivorn, "ivo://auth/%s#local" % (char, ))
