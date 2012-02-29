import struct

from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet.protocol import ServerFactory

from ..protocol import ElementSender

class DummyElement(object):
    text = "Dummy Text"

class ElementSenderFactory(ServerFactory):
    protocol = ElementSender

class ElementSenderTestCase(unittest.TestCase):
    def setUp(self):
        factory = ElementSenderFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_send_xml(self):
        dummy_element = DummyElement()
        self.proto.send_xml(dummy_element)
        self.assertEqual(
            self.tr.value(),
            struct.pack("!i", len(dummy_element.text)) + dummy_element.text
        )

    def test_lengthLimitExceeded(self):
        dummy_element = DummyElement()
        self.proto.dataReceived(
            struct.pack("<i", len(dummy_element.text)) + dummy_element.text
        )
        self.assertEqual(self.tr.disconnecting, True)
