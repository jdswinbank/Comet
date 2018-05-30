# Comet VOEvent Broker.
# Tests for master broker service.

from ipaddress import ip_network

from twisted.trial import unittest
from twisted.python import usage
from twisted.internet import reactor

import comet.log as log

from comet.service.broker import BCAST_TEST_INTERVAL
from comet.service.broker import DEFAULT_REMOTE_PORT
from comet.service.broker import Options
from comet.service.broker import makeService
from comet.testutils import DUMMY_SERVICE_IVOID

class DefaultOptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()
        # Note that parsing from the command line always results in a str,
        # regardless of whether we're running Python 2.
        self.cmd_line = ["--local-ivo", DUMMY_SERVICE_IVOID.decode()]

    def test_faulty_cmd_line(self):
        self.cmd_line.append("--not-a-real-option")
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            self.cmd_line
        )

    def test_test_event_loop(self):
        self.assertEqual(self.config['broadcast-test-interval'], BCAST_TEST_INTERVAL)
        self.cmd_line.extend(["--broadcast-test-interval", "0"])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['broadcast-test-interval'], 0)

    def test_enable_receive(self):
        self.assertFalse(self.config['receive'])
        self.cmd_line.append("--receive")
        self.config.parseOptions(self.cmd_line)
        self.assertTrue(self.config['receive'])

    def test_enable_broadcast(self):
        self.assertFalse(self.config['broadcast'])
        self.cmd_line.append("--broadcast")
        self.config.parseOptions(self.cmd_line)
        self.assertTrue(self.config['broadcast'])

    def test_remotes(self):
        HOST0, PORT = "dummy_0", 0
        HOST1 = "dummy_1"
        self.cmd_line.extend(["--remote", "%s:%d" % (HOST0, PORT), "--remote", HOST1])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['remotes']), 2)
        self.assertTrue((HOST0, PORT) in self.config['remotes'])
        self.assertTrue((HOST1, DEFAULT_REMOTE_PORT) in self.config['remotes'])

    def _test_empty_whitelist(self, whitelist_name):
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config[whitelist_name], [ip_network("0.0.0.0/0")])

    def test_default_broadcast_whitelist(self):
        self._test_empty_whitelist('subscriber-whitelist')

    def test_default_submission_whitelist(self):
        self._test_empty_whitelist('author-whitelist')

    def _test_populated_whitelist(self, whitelist_name):
        net1, net2 = "1.2.3.4/32", "4.3.2.1/255.255.0.0"
        cmd_line_flag = "--%s" % (whitelist_name,)
        self.cmd_line.extend([cmd_line_flag, net1, cmd_line_flag, net2])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config[whitelist_name]), 2)
        for net in [net1, net2]:
            self.assertTrue(
                ip_network(net, strict=False) in self.config[whitelist_name]
            )

    def test_populated_broadcast_whitelist(self):
        self._test_populated_whitelist('subscriber-whitelist')

    def test_populated_submission_whitelist(self):
        self._test_populated_whitelist('author-whitelist')

    def test_has_print_event_plugin(self):
        self.cmd_line.append("--print-event")
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 1)
        self.assertEqual(self.config['handlers'][0].name, "print-event")

    def test_has_save_event_plugin(self):
        self.cmd_line.append("--save-event")
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 1)
        self.assertEqual(self.config['handlers'][0].name, "save-event")

    def test_save_event_plugin_takes_args(self):
        self.cmd_line.extend(["--save-event", "--save-event-directory=/tmp"])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['handlers'][0].name, "save-event")
        self.assertEqual(self.config['handlers'][0].directory, "/tmp")

    def test_args_for_disabled_plugin(self):
        # Should not enable the plugin
        self.cmd_line.append("--save-event-directory=/tmp")
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 0)

    def test_action_non_extant(self):
        action = "does-not-exist"
        self.cmd_line.extend(["--action", action])
        self.assertRaises(usage.UsageError, self.config.parseOptions, self.cmd_line)

    def test_filters(self):
        self.cmd_line.extend(["--filter", "foo", "--filter", "bar"])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['filters']), 2)

    def test_invalid_filter(self):
        self.cmd_line.extend(["--filter", "not(starts-with("])
        self.assertRaises(usage.UsageError, self.config.parseOptions, self.cmd_line)

    def test_cmd(self):
        self.cmd_line.extend(["--cmd", "foo", "--cmd", "bar"])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['handlers']), 2)

    def test_verbose_default(self):
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(log.LEVEL, log.DEFAULT_LEVEL)

    def test_verbose_verbose(self):
        self.cmd_line.append('-v')
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(log.LEVEL, log.Levels.DEBUG)

    def test_verbose_quiet(self):
        self.cmd_line.append('-q')
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(log.LEVEL, log.Levels.WARNING)

    def test_verbose_contradictory(self):
        self.cmd_line.extend(['-q', '-v'])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(log.LEVEL, log.DEFAULT_LEVEL)

    def test_valid_ivoid(self):
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['local-ivo'], DUMMY_SERVICE_IVOID.decode())

    def test_invalid_ivoid(self):
        self.cmd_line.extend(["--local-ivo", "ivo://"])
        self.assertRaises(usage.UsageError, self.config.parseOptions, self.cmd_line)

    def test_ivoid_missing(self):
        # It's fine not to provide an IVOID on the command line as of the VTP2
        # spec, as long as we're only operating as a subscriber.
        self.config.parseOptions("")

        # But it's required if we act as broadcaster or receiver.
        self.assertRaises(usage.UsageError, self.config.parseOptions, "-b")
        self.assertRaises(usage.UsageError, self.config.parseOptions, "-r")


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()

    def _make_service(self, options):
        self.config.parseOptions(options)
        return makeService(self.config)

    def test_has_receiver(self):
        service = self._make_service(['--local-ivo', 'ivo://comet/test', '-r',
                                      '-b', '--remote', 'dummy'])
        for service_name in (
            "Receiver", "Broadcaster",
            "Remote %s:%d" % ('dummy', DEFAULT_REMOTE_PORT)
        ):
            self.assertTrue(service_name in service.namedServices)

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
