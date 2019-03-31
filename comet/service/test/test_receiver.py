# Comet VOEvent Broker.
# Tests for event receiver service.

from ipaddress import ip_network

from twisted.internet.endpoints import serverFromString
from twisted.test import proto_helpers
from twisted.trial import unittest

from comet.service import makeReceiverService

class ReceiverServiceTestCase(unittest.TestCase):
    """Check for correct operation of the VOEvent receiver service."""

    def setUp(self):
        self.reactor = proto_helpers.MemoryReactor()

    def test_tcp_listen(self):
        """Demonstrate that the service listens on a TCP socket."""
        self.assertEqual(len(self.reactor.tcpServers), 0)
        port = 12345
        ep = serverFromString(self.reactor, f"tcp:{port}")
        service = makeReceiverService(ep, "ivo://foo/bar", [], [],
                                      [ip_network("0.0.0.0/0")])
        service.startService()
        self.assertEqual(len(self.reactor.tcpServers), 1)
        self.assertEqual(self.reactor.tcpServers[0][0], port)

    def test_unix_listen(self):
        """Demonstrate that the service listens on a Unix domain socket."""
        self.assertEqual(len(self.reactor.unixServers), 0)
        path = "/dev/null"
        ep = serverFromString(self.reactor, f"unix:{path}")
        service = makeReceiverService(ep, "ivo://foo/bar", [], [], [])
        service.startService()
        self.assertEqual(len(self.reactor.unixServers), 1)
        self.assertEqual(self.reactor.unixServers[0][0], path)
