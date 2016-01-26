# Comet VOEvent Broker.
# Tests for VTP messages.

import os
import lxml.etree as etree
from twisted.trial import unittest

import comet
from comet.testutils import DUMMY_SERVICE_IVORN

from comet.protocol.messages import (iamalive, iamaliveresponse, ack, nak,
                                     authenticate, authenticateresponse)

class TransportTestCase(unittest.TestCase):

    def setUp(self):
        self.schema = etree.XMLSchema(
            etree.parse(
                os.path.join(comet.__path__[0], "schema/transport-1.1.xsd")
            )
        )

    def test_iamalive_valid(self):
        message = iamalive(DUMMY_SERVICE_IVORN)
        self.assertTrue(self.schema.validate(message.element))

    def test_iamaliveresponse_valid(self):
        message = iamaliveresponse(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN)
        self.assertTrue(self.schema.validate(message.element))

    def test_ack_valid(self):
        message = ack(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN)
        self.assertTrue(self.schema.validate(message.element))

    def test_nak_valid(self):
        message = nak(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN)
        self.assertTrue(self.schema.validate(message.element))

    def test_nak_with_result_valid(self):
        message = nak(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN, "reason")
        self.assertTrue(self.schema.validate(message.element))

    def test_authenticate_valid(self):
        message = authenticate(DUMMY_SERVICE_IVORN)
        self.assertTrue(self.schema.validate(message.element))

    def test_authenticateresponse_valid(self):
        message = authenticateresponse(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN, [])
        self.assertTrue(self.schema.validate(message.element))

    def test_authenticateresponse_valid_filter(self):
        filters = ["test1<>?!", "test2<>?!"]
        message = authenticateresponse(DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN, filters)
        filter_elems = message.findall("Meta/Param[@name=\"xpath-filter\"]")
        for inp, outp in zip(filters, filter_elems):
            self.assertEqual(inp, outp.get('value'))
        self.assertTrue(self.schema.validate(message.element))
