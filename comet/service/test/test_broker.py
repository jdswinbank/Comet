# Comet VOEvent Broker.
# Tests for master broker service.

import os.path

from contextlib import redirect_stderr
from ipaddress import ip_network

from twisted.trial import unittest
from twisted.python import usage
from twisted.internet import reactor

from comet.service.broker import BCAST_TEST_INTERVAL
from comet.service.broker import DEFAULT_SUBMIT_PORT
from comet.service.broker import DEFAULT_SUBSCRIBE_PORT
from comet.service.broker import Options
from comet.service.broker import makeService
from comet.testutils import DUMMY_SERVICE_IVOID

class BrokerOptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()
        self.cmd_line = ["--local-ivo", DUMMY_SERVICE_IVOID.decode()]

    def _check_bad_parse(self, cmd_line):
        # A bad parse will raise `builtins.SystemExit` and spew to stderr.
        # Catch the latter so it doesn't appear in the logs.
        with redirect_stderr(open('/dev/null', 'w')):
            self.assertRaises(SystemExit, self.config.parseOptions, cmd_line)

    def _check_server_endpoints(self, option_name, default_port):
        # Check for a set of server endpoints specifed by ``--option_name``.

        # If not specified, we shouldn't receive at all.
        self.config.parseOptions(self.cmd_line)
        self.assertIsNone(self.config[option_name])

        # If specified with no argument, use the default endpoint.
        self.config.parseOptions(self.cmd_line + [f"--{option_name}"])
        self.assertEqual(len(self.config[option_name]), 1)
        self.assertEqual(self.config[option_name][0]._port, default_port)

        # If specified with an argument, use that.
        self.config.parseOptions(self.cmd_line + [f"--{option_name}", "tcp:1"])
        self.assertEqual(len(self.config[option_name]), 1)
        self.assertEqual(self.config[option_name][0]._port, 1)

        # If specified with an argument AND without, do both.
        self.config.parseOptions(self.cmd_line +
                                 [f"--{option_name}",
                                  f"--{option_name}", "tcp:1"])
        self.assertEqual(len(self.config[option_name]), 2)
        self.assertEqual(self.config[option_name][0]._port, default_port)
        self.assertEqual(self.config[option_name][1]._port, 1)

        # And it should work with a Unix domain socket.
        self.config.parseOptions(self.cmd_line + [f"--{option_name}",
                                                  "unix:/test"])
        self.assertEqual(len(self.config[option_name]), 1)
        self.assertEqual(self.config[option_name][0]._address, "/test")

        # But not with garbage.
        self._check_bad_parse(self.cmd_line + [f"--{option_name}", "bad"])

    def _check_whitelist(self, option_name):
        # Check that ``option_name`` corresponds to a default-allow whitelist.

        def check_wl_contents(wl, expected_values):
            # Check the contents of a whitelist against a model
            self.assertEqual(len(wl), len(expected_values))
            for net in expected_values:
                self.assertIn(net, wl)

        config_name = option_name.replace("-", "_")
        NET_DEFAULT, NET1, NET2 = "0.0.0.0/0", "10.0.0.0/8", "172.16.0.0/12"

        # By default, everything is whitelisted.
        self.config.parseOptions(self.cmd_line)
        check_wl_contents(self.config[config_name],
                          [ip_network(NET_DEFAULT)])

        # If a single argument is supplied, it replaces the default.
        self.config.parseOptions(self.cmd_line +
                                 [f"--{option_name}", NET1])
        check_wl_contents(self.config[config_name], [ip_network(NET1)])

        # If two arguments is supplied, use both
        self.config.parseOptions(self.cmd_line +
                                 [f"--{option_name}", NET1, NET2])
        check_wl_contents(self.config[config_name],
                          [ip_network(NET1), ip_network(NET2)])

        # If --receive-whitelist is supplied twice, use only the second.
        self.config.parseOptions(self.cmd_line +
                                 [f"--{option_name}", NET1,
                                  f"--{option_name}", NET2])
        check_wl_contents(self.config[config_name], [ip_network(NET2)])

    def test_return_self(self):
        # parseOptions() should return `self.config` for convenience.
        self.assertEqual(self.config, self.config.parseOptions(self.cmd_line))

    def test_local_ivoid(self):
        # The local IVOID should be set correctly.
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['local_ivo'], DUMMY_SERVICE_IVOID.decode())

        # And a bad one rejected.
        self._check_bad_parse(["--local-ivo", "bad_ivo"])

    def test_ivoid_required(self):
        # A local IVOID is not required _unless_ a broadcaster and/or a
        # receiver is running.

        # Should be fine
        self.config.parseOptions(self.cmd_line + ["--receive"])
        self.config.parseOptions(self.cmd_line + ["--broadcast"])
        self.config.parseOptions(self.cmd_line + ["--broadcast", "--receive"])

        # Should fail
        self._check_bad_parse(["--receive"])
        self._check_bad_parse(["--broadcast"])
        self._check_bad_parse(["--receive", "--broadcast"])

    def test_eventdb(self):
        # Default value should be a directory.
        self.assertTrue(os.path.isdir(self.config.parseOptions(self.cmd_line)
                                      ['eventdb']))

        # Specifying our own directory should also work.
        dirname = "/example"
        self.assertEqual(self.config.parseOptions(["--eventdb", dirname])['eventdb'],
                         dirname)

    def test_receive(self):
        # Check that ``--receive`` properly sets up server endpoints.
        self._check_server_endpoints("receive", DEFAULT_SUBMIT_PORT)

    def test_receive_whitelist(self):
        # Check that we create a whitelist for receivers.
        self._check_whitelist("receive-whitelist")

    def test_broadcast(self):
        # Check that ``--broadcast`` properly sets up server endpoints.
        self._check_server_endpoints("broadcast", DEFAULT_SUBSCRIBE_PORT)

    def test_broadcast_test_interval(self):
        # Check that the default is set.
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['broadcast_test_interval'],
                         BCAST_TEST_INTERVAL)

        # And can be over-ridden.
        self.config.parseOptions(self.cmd_line +
                                 ["--broadcast-test-interval", 0])
        self.assertEqual(self.config['broadcast_test_interval'], 0)

    def test_broadcast_whitelist(self):
        # Check that we create a whitelist for broadcasters.
        self._check_whitelist("broadcast-whitelist")

    def test_subscribe(self):
        # By default, we subscribe to nothing.
        self.config.parseOptions(self.cmd_line)
        self.assertIsNone(self.config['subscribe'])

        # --subscribe always requires an egument.
        self._check_bad_parse(self.cmd_line + ["--subscribe"])

        # Specifying a single endpoint should add that to the list of
        # subcribers.
        self.config.parseOptions(self.cmd_line +
                                 ["--subscribe",
                                  f"tcp:test:{DEFAULT_SUBSCRIBE_PORT}"])
        self.assertEqual(len(self.config['subscribe']), 1)
        self.assertEqual(self.config['subscribe'][0]._port,
                         DEFAULT_SUBSCRIBE_PORT)
        self.assertEqual(self.config['subscribe'][0]._host, "test")

        # Specifying multiple endpoints to a single --subscribe option should
        # fail to parse.
        self._check_bad_parse(self.cmd_line + [f"--subscribe",
                                               f"tcp:test:{DEFAULT_SUBSCRIBE_PORT}",
                                               f"tcp:test2:{DEFAULT_SUBSCRIBE_PORT}"])

        # Specifying multiple endpoints to with multiple --subscribe options
        # should succeed.
        self.config.parseOptions(self.cmd_line +
                                 [f"--subscribe",
                                  f"tcp:test:{DEFAULT_SUBSCRIBE_PORT}",
                                  f"--subscribe",
                                  f"tcp:test2:{DEFAULT_SUBSCRIBE_PORT+1}"])
        self.assertEqual(len(self.config['subscribe']), 2)
        self.assertEqual(self.config['subscribe'][0]._port,
                         DEFAULT_SUBSCRIBE_PORT)
        self.assertEqual(self.config['subscribe'][0]._host, "test")
        self.assertEqual(self.config['subscribe'][1]._port,
                         DEFAULT_SUBSCRIBE_PORT + 1)
        self.assertEqual(self.config['subscribe'][1]._host, "test2")

    def test_filter(self):
       # By default, no filters are specified.
       self.config.parseOptions(self.cmd_line)
       self.assertIsNone(self.config['filters'])

       # A single valid XPath expression should be accepted as a filter.
       self.config.parseOptions(self.cmd_line + ["--filter", "foo"])
       self.assertEqual(len(self.config['filters']), 1)
       self.assertEqual(self.config['filters'][0], "foo")

       # Multiple valid XPath expressions should be accepted.
       self.config.parseOptions(self.cmd_line + ["--filter", "foo",
                                                 "--filter", "bar"])
       self.assertEqual(len(self.config['filters']), 2)
       self.assertIn("foo", self.config['filters'])
       self.assertIn("bar", self.config['filters'])

       # But each ``--filter`` option only takes one argument.
       self._check_bad_parse(self.cmd_line + ["--filter", "foo", "bar"])

       # An invalid filter should be rejected.
       self._check_bad_parse(self.cmd_line + ["--filter", "\/\/\/\/"])

    def test_cmd(self):
        # By default, no handlers are specified.
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 0)

        # A single cmd results in a single handler.
        self.config.parseOptions(self.cmd_line + ["--cmd", "foo"])
        self.assertEqual(len(self.config['handlers']), 1)
        self.assertEqual(self.config['handlers'][0].cmd, "foo")

        # Multiple cmds may be specified
        self.config.parseOptions(self.cmd_line + ["--cmd", "foo",
                                                  "--cmd", "bar"])
        self.assertEqual(len(self.config['handlers']), 2)
        self.assertEqual(self.config['handlers'][0].cmd, "foo")
        self.assertEqual(self.config['handlers'][1].cmd, "bar")

        # But each ``--cmd`` option only takes one argument.
        self._check_bad_parse(self.cmd_line + ["--cmd", "foo", "bar"])

    def test_has_print_event_plugin(self):
        self.config.parseOptions(self.cmd_line + ["--print-event"])
        self.assertEqual(len(self.config['handlers']), 1)
        self.assertEqual(self.config['handlers'][0].name, "print-event")

    def test_has_save_event_plugin(self):
        self.config.parseOptions(self.cmd_line + ["--save-event"])
        self.assertEqual(len(self.config['handlers']), 1)
        self.assertEqual(self.config['handlers'][0].name, "save-event")

    def test_save_event_plugin_takes_args(self):
        ["--save-event", "--save-event-directory=/tmp"]
        self.config.parseOptions(self.cmd_line +
                                 ["--save-event",
                                  "--save-event-directory=/tmp"])
        self.assertEqual(self.config['handlers'][0].name, "save-event")
        self.assertEqual(self.config['handlers'][0].directory, "/tmp")

    def test_args_for_disabled_plugin(self):
        # Should not enable the plugin
        self.cmd_line.append("--save-event-directory=/tmp")
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 0)


class BrokerServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()

    def _make_service(self, options):
        self.config.parseOptions(options)
        return makeService(self.config)

    def test_has_services(self):
        # Demonstrate that we can create appropriate numbers of services.

        # A single receiver.
        service = self._make_service(['--local-ivo', 'ivo://comet/test',
                                      '--receive'])
        self.assertEqual(len(service.services), 1)

        # A single broadcaster.
        service = self._make_service(['--local-ivo', 'ivo://comet/test',
                                      '--broadcast'])
        self.assertEqual(len(service.services), 1)

        # A single subscriber.
        service = self._make_service(['--local-ivo', 'ivo://comet/test',
                                      '--subscribe', "tcp:test:12345"])
        self.assertEqual(len(service.services), 1)

        # All of the above.
        service = self._make_service(['--local-ivo', 'ivo://comet/test',
                                      '--receive', '--broadcast',
                                      '--subscribe', "tcp:test:12345"])
        self.assertEqual(len(service.services), 3)

        # Multiple instances of each service.
        service = self._make_service(['--local-ivo', 'ivo://comet/test',
                                      '--receive', '--broadcast',
                                      '--receive', 'tcp:1234',
                                      '--broadcast', 'tcp:4321',
                                      '--subscribe', "tcp:test:12345",
                                      '--subscribe', "tcp:test:54321"])
        self.assertEqual(len(service.services), 6)

    def test_no_service(self):
        # When we ask for no services on the command line, nothing should be
        # started -- but we also shouldn't raise.
        # Note we need to stub out the reactor's callWhenRunning() method,
        # because makeService schedules a reactor.stop() which will bring our
        # test cases crashing down.
        oldCallWhenRunning = reactor.callWhenRunning
        class MockCallWhenRunning(object):
            def __init__(self):
                self.call_count = 0

            def __call__(self, *args, **kwargs):
                self.call_count += 1
        mockCallWhenRunning = MockCallWhenRunning()
        try:
            reactor.callWhenRunning = mockCallWhenRunning
            service = self._make_service(['--local-ivo', 'ivo://comet/test'])
        finally:
            # Be sure to return the reactor to its initial state when done.
            reactor.callWhenRunning = oldCallWhenRunning

        # No services created.
        self.assertEqual(len(service.namedServices), 0)
        # Should have been called twice: once for logging, once to stop the
        # reactor. We are not actually checking the values of those calls
        # here, though.
        self.assertEqual(mockCallWhenRunning.call_count, 2)

    def tearDown(self):
        for call in reactor.getDelayedCalls():
            call.cancel()
