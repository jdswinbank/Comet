from twisted.internet import reactor
from twisted.trial import unittest

from comet.utility import coerce_to_client_endpoint, coerce_to_server_endpoint


class coerce_to_client_endpoint_TestCase(unittest.TestCase):
    HOST, PORT, DEFAULT_PORT = "test", 1234, 4321

    def test_good_tcp_parse(self):
        ep = coerce_to_client_endpoint(
            reactor, f"tcp:{self.HOST}:{self.PORT}", self.DEFAULT_PORT
        )
        self.assertEqual(ep._host, self.HOST)
        self.assertEqual(ep._port, self.PORT)

    def test_good_unix_parse(self):
        filename = "/dev/null"
        ep = coerce_to_client_endpoint(reactor, f"unix:{filename}", self.DEFAULT_PORT)
        self.assertEqual(ep._path, filename)

    def test_missing_protocol(self):
        ep = coerce_to_client_endpoint(
            reactor, f"{self.HOST}:{self.PORT}", self.DEFAULT_PORT
        )
        self.assertEqual(ep._host, self.HOST)
        self.assertEqual(ep._port, self.PORT)

    def test_missing_port(self):
        ep = coerce_to_client_endpoint(reactor, f"tcp:{self.HOST}", self.DEFAULT_PORT)
        self.assertEqual(ep._host, self.HOST)
        self.assertEqual(ep._port, self.DEFAULT_PORT)

    def test_missing_both(self):
        ep = coerce_to_client_endpoint(reactor, self.HOST, self.DEFAULT_PORT)
        self.assertEqual(ep._host, self.HOST)
        self.assertEqual(ep._port, self.DEFAULT_PORT)

    def test_bad_parse(self):
        self.assertRaises(
            ValueError,
            coerce_to_client_endpoint,
            reactor,
            "tcp:tcp:tcp",
            self.DEFAULT_PORT,
        )


class coerce_to_server_endpoint_TestCase(unittest.TestCase):
    PORT = 1234

    def test_good_tcp_parse(self):
        ep = coerce_to_server_endpoint(reactor, f"tcp:{self.PORT}")
        self.assertEqual(ep._port, self.PORT)

    def test_good_unix_parse(self):
        filename = "/dev/null"
        ep = coerce_to_server_endpoint(reactor, f"unix:{filename}")
        self.assertEqual(ep._address, filename)

    def test_missing_protocol(self):
        ep = coerce_to_server_endpoint(reactor, self.PORT)
        self.assertEqual(ep._port, self.PORT)

    def test_bad_parse(self):
        self.assertRaises(ValueError, coerce_to_server_endpoint, reactor, "tcp:")
