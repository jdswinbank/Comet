from ipaddr import IPNetwork
from lxml.etree import XPath

from twisted.trial import unittest
from twisted.python import usage
from twisted.internet import reactor

from ...utility import log

from ..broker import BCAST_TEST_INTERVAL
from ..broker import DEFAULT_REMOTE_PORT
from ..broker import Options
from ..broker import makeService
from comet.test.support import DUMMY_SERVICE_IVORN

class DefaultOptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()
        self.cmd_line = ["--local-ivo", DUMMY_SERVICE_IVORN]

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

    def test_default_whitelist(self):
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['whitelist'], [IPNetwork("0.0.0.0/0")])

    def test_specified_whitelist(self):
        net1, net2 = "1.2.3.4/32", "4.3.2.1/255.255.0.0"
        self.cmd_line.extend(["--whitelist", net1, "--whitelist", net2])
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(len(self.config['whitelist']), 2)
        for net in [net1, net2]:
            self.assertTrue(IPNetwork(net) in self.config['whitelist'])

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

    def test_valid_ivorn(self):
        self.config.parseOptions(self.cmd_line)
        self.assertEqual(self.config['local-ivo'], DUMMY_SERVICE_IVORN)

    def test_invalid_ivorn(self):
        self.cmd_line.extend(["--local-ivo", "ivo://"])
        self.assertRaises(usage.UsageError, self.config.parseOptions, self.cmd_line)

    def test_ivorn_missing(self):
        self.assertRaises(usage.UsageError, self.config.parseOptions, "")


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        config = Options()
        config.parseOptions(['--local-ivo', 'ivo://comet/test', '-r', '-b', '--remote', 'dummy'])
        self.service = makeService(config)

    def test_has_receiver(self):
        for service in (
            "Receiver", "Broadcaster",
            "Remote %s:%d" % ('dummy', DEFAULT_REMOTE_PORT)
        ):
            self.assertTrue(self.service.namedServices.has_key(service))

    def tearDown(self):
        for call in reactor.getDelayedCalls():
            call.cancel()
