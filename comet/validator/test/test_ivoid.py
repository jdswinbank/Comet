# Comet VOEvent Broker.
# Test to weed out bad IVOIDs.

from twisted.trial import unittest

from comet.icomet import IValidator
from comet.utility import xml_document
from comet.validator import CheckIVOID
from comet.testutils import DUMMY_VOEVENT, DUMMY_EVENT_IVOID

BAD_EVENT_TEXT = u"""
<voe:VOEvent xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0
  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test"
  ivorn="ivo://comet.broker/test#">
  <Who>
    <AuthorIVORN>ivo://comet.broker/test</AuthorIVORN>
  </Who>
</voe:VOEvent>
""".encode("utf-8")

class CheckSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = CheckIVOID()

    def test_valid(self):
        # Should not raise
        self.validator(xml_document(DUMMY_VOEVENT))

    def test_invalid(self):
        self.assertRaises(Exception, self.validator,
            xml_document(BAD_EVENT_TEXT.replace(DUMMY_EVENT_IVOID, b"bad_ivoid"))
        )

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.validator))
