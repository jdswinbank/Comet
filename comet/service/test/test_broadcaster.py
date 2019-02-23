# Comet VOEvent Broker.
# Tests for event broadcaster service.

from ipaddress import ip_network

from twisted.trial import unittest
from twisted.test import proto_helpers
from comet.service import makeBroadcasterService

class BroadcasterServiceTestCase(unittest.TestCase):
    """Check for correct operation of the VOEvent broadcaster service."""

    def setUp(self):
        self.reactor = proto_helpers.MemoryReactor()

    def test_tcp_listn(self):
        """Demonstrate that the service listens on a TCP socket."""
        port = 8099
        self.assertEqual(len(self.reactor.tcpServers), 0)
        service = makeBroadcasterService(self.reactor, f"tcp:{port}",
                                         "ivo://foo/bar", 0,
                                         [ip_network("0.0.0.0/0")])
        service.startService()
        self.assertEqual(len(self.reactor.tcpServers), 1)
        self.assertEqual(self.reactor.tcpServers[0][0], port)


    def test_unix_listens(self):
        """Demonstrate that the service connects to a Unix domain socket."""
        self.assertEqual(len(self.reactor.unixServers), 0)
        path = "/dev/null"
        service = makeBroadcasterService(self.reactor, f"unix:{path}",
                                         "ivo://foo/bar", 0, [])
        service.startService()
        self.assertEqual(len(self.reactor.unixServers), 1)
        self.assertEqual(self.reactor.unixServers[0][0], path)
