import os

from twisted.trial import unittest

import comet
from comet.icomet import IValidator
from comet.utility.xml import xml_document
from comet.validator.ivorn import CheckIVORN
from comet.test.support import DUMMY_VOEVENT, DUMMY_EVENT_IVORN

BAD_EVENT_TEXT = """
<voe:VOEvent xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0
  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test"
  ivorn="ivo://comet.broker/test#">
  <Who>
    <AuthorIVORN>ivo://comet.broker/test</AuthorIVORN>
  </Who>
</voe:VOEvent>
"""

class CheckSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = CheckIVORN()

    def test_valid(self):
        # Should not raise
        self.validator(xml_document(DUMMY_VOEVENT))

    def test_invalid(self):
        self.assertRaises(Exception, self.validator,
            xml_document(BAD_EVENT_TEXT.replace(DUMMY_EVENT_IVORN, "bad_ivorn"))
        )

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.validator))
