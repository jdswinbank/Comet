# Comet VOEvent Broker.
# Tests for event schema validator.

import os

from twisted.trial import unittest

import comet
from comet.icomet import IValidator
from comet.utility import xml_document
from comet.validator import CheckSchema
from comet.testutils import DUMMY_VOEVENT

BAD_EVENT_TEXT = b"""<xml></xml>"""

class CheckSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = CheckSchema(
            os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
        )

    def test_valid(self):
        return self.validator(xml_document(DUMMY_VOEVENT))

    def test_invalid(self):
        d = self.validator(xml_document(BAD_EVENT_TEXT))
        return self.assertFailure(d, Exception)

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.validator))
