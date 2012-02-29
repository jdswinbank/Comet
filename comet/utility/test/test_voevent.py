import os
import lxml.etree as etree

from twisted.trial import unittest

from ...test.support import DUMMY_SERVICE_IVORN as DUMMY_IVORN

import comet
from ..voevent import broker_test_message

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
