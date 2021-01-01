# Comet VOEvent Broker.
# Tests for VTP messages.

import os
from datetime import datetime

import lxml.etree as etree
from twisted.trial import unittest

import comet
from comet.testutils import DUMMY_SERVICE_IVOID
from comet.protocol.messages import TransportMessage


class TransportTestCase(unittest.TestCase):
    def setUp(self):
        self.schema = etree.XMLSchema(
            etree.parse(os.path.join(comet.__path__[0], "schema/transport-1.1.xsd"))
        )

    def _check_message(self, message, role):
        """
        Check that the provided message:

        - Is valid per the transport schema;
        - Has all TimeStamps marked as UTC (ie, with a 'Z' suffix);
        - Has the right role.
        """
        self.assertTrue(self.schema.validate(message.element))
        for timestamp in message.element.findall("TimeStamp"):
            datetime.strptime(timestamp.text, "%Y-%m-%dT%H:%M:%SZ")
        self.assertEqual(message.role, role)

    def test_iamalive_valid(self):
        self._check_message(TransportMessage.iamalive(DUMMY_SERVICE_IVOID), "iamalive")

    def test_iamaliveresponse_valid(self):
        self._check_message(
            TransportMessage.iamaliveresponse(DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID),
            "iamalive",
        )

    def test_ack_valid(self):
        self._check_message(
            TransportMessage.ack(DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID), "ack"
        )

    def test_nak_valid(self):
        self._check_message(
            TransportMessage.nak(DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID), "nak"
        )

    def test_nak_with_result_valid(self):
        self._check_message(
            TransportMessage.nak(DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID, "reason"),
            "nak",
        )

    def test_authenticate_valid(self):
        self._check_message(
            TransportMessage.authenticate(DUMMY_SERVICE_IVOID), "authenticate"
        )

    def test_authenticateresponse_valid(self):
        self._check_message(
            TransportMessage.authenticateresponse(
                DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID, []
            ),
            "authenticate",
        )

    def test_authenticateresponse_valid_filter(self):
        filters = ["test1<>?!", "test2<>?!"]
        message = TransportMessage.authenticateresponse(
            DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID, filters
        )
        filter_elems = message.element.findall('Meta/Param[@name="xpath-filter"]')
        for inp, outp in zip(filters, filter_elems):
            self.assertEqual(inp, outp.get("value"))
        self._check_message(message, "authenticate")
