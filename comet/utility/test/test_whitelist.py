# Comet VOEvent Broker.
# Test for IP whitelisting system.

from ipaddress import ip_network

from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet.address import IPv4Address
from twisted.python import log as twisted_log
from twisted.trial import unittest

from comet.utility import WhitelistingFactory
from comet.testutils import DummyLogObserver

class TestFactory(ServerFactory):
    protocol = Protocol

class WhitelistingFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.observer = DummyLogObserver()
        twisted_log.addObserver(self.observer)

    def tearDown(self):
        twisted_log.removeObserver(self.observer)

    def test_empty_whitelist(self):
        # All connections should be denied and a default message logged.
        factory = WhitelistingFactory(TestFactory(), [])
        self.assertEqual(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.1', 0)),
            None
        )
        self.assertEqual(len(self.observer.messages), 1)
        self.assertTrue("connection" in self.observer.messages[0][0])

    def test_in_whitelist(self):
        # Connection should be accepted and nothing logged.
        factory = WhitelistingFactory(TestFactory(), [ip_network('0.0.0.0/0')])
        self.assertIsInstance(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.1', 0)),
            Protocol
        )
        self.assertEqual(len(self.observer.messages), 0)

    def test_not_in_whitelist(self):
        # Connection should be accepted and nothing logged.
        factory = WhitelistingFactory(TestFactory(), [ip_network('127.0.0.1/32')])
        self.assertEqual(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.2', 0)),
            None
        )

    def test_log_message(self):
        # Should be possible to customize the message which is logged.
        TEST_STRING = "test-1234"
        factory = WhitelistingFactory(
            TestFactory(), [ip_network('127.0.0.1/32')], TEST_STRING
        )
        self.assertEqual(
            factory.buildProtocol(IPv4Address('TCP', '127.0.0.2', 0)),
            None
        )
        self.assertFalse("connection" in self.observer.messages[0][0])
        self.assertTrue(TEST_STRING in self.observer.messages[0][0])
