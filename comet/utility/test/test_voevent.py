import os
import lxml.etree as etree

from twisted.trial import unittest

import comet
from ..voevent import broker_test_message

DUMMY_IVORN = "ivo://comet.broker/test"

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
