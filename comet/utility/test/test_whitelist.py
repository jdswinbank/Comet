from ipaddr import IPNetwork

from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet.address import IPv4Address
from twisted.trial import unittest

from ...test.support import DummyEvent

from ..whitelist import WhitelistingFactory

class TestFactory(ServerFactory):
    protocol = Protocol

class WhitelistingFactoryTestCase(unittest.TestCase):
    def test_empty_whitelist(self):
        # All connections should be denied
        factory = WhitelistingFactory(TestFactory(), [])
        self.assertEqual(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.1', 0)),
            None
        )

    def test_in_whitelist(self):
        factory = WhitelistingFactory(TestFactory(), [IPNetwork('0.0.0.0/0')])
        self.assertIsInstance(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.1', 0)),
            Protocol
        )

    def test_not_in_whitelist(self):
        factory = WhitelistingFactory(TestFactory(), [IPNetwork('127.0.0.1/32')])
        self.assertEqual(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.2', 0)),
            None
        )
