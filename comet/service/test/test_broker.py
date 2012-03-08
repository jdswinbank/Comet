from ipaddr import IPNetwork

from twisted.trial import unittest
from twisted.python import usage
from twisted.internet import reactor

from ...log import log

from ..broker import DEFAULT_REMOTE_PORT
from ..broker import Options
from ..broker import makeService

class DefaultOptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Options()

    def test_faulty_cmd_line(self):
        cmd_line = ["--not-a-real-option"]
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            cmd_line
        )

    def test_enable_receive(self):
        self.assertFalse(self.config['receive'])
        cmd_line = ["--receive"]
        self.config.parseOptions(cmd_line)
        self.assertTrue(self.config['receive'])

    def test_enable_broadcast(self):
        self.assertFalse(self.config['broadcast'])
        cmd_line = ["--broadcast"]
        self.config.parseOptions(cmd_line)
        self.assertTrue(self.config['broadcast'])

    def test_remotes(self):
        HOST0, PORT = "dummy_0", 0
        HOST1 = "dummy_1"
        cmd_line = ["--remote", "%s:%d" % (HOST0, PORT), "--remote", HOST1]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['remotes']), 2)
        self.assertTrue((HOST0, PORT) in self.config['remotes'])
        self.assertTrue((HOST1, DEFAULT_REMOTE_PORT) in self.config['remotes'])

    def test_default_whitelist(self):
        self.config.postOptions()
        self.assertEqual(self.config['whitelist'], [IPNetwork("0.0.0.0/0")])

    def test_specified_whitelist(self):
        net1, net2 = "1.2.3.4/32", "4.3.2.1/255.255.0.0"
        cmd_line = ["--whitelist", net1, "--whitelist", net2]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['whitelist']), 2)
        for net in [net1, net2]:
            self.assertTrue(IPNetwork(net) in self.config['whitelist'])

    def test_action_extant(self):
        action = "print-event"
        cmd_line = ["--action", action]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['handlers']), 1)

    def test_action_non_extant(self):
        action = "does-not-exist"
        cmd_line = ["--action", action]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['handlers']), 0)

    def test_filters(self):
        cmd_line = ["--filter", "foo", "--filter", "bar"]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['filters']), 2)

    def test_cmd(self):
        cmd_line = ["--cmd", "foo", "--cmd", "bar"]
        self.config.parseOptions(cmd_line)
        self.assertEqual(len(self.config['handlers']), 2)

    def test_verbose_default(self):
        self.config.parseOptions([])
        self.assertEqual(log.LEVEL, log.DEFAULT_LEVEL)

    def test_verbose_verbose(self):
        cmd_line = ['-v']
        self.config.parseOptions(cmd_line)
        self.assertEqual(log.LEVEL, log.Levels.DEBUG)

    def test_verbose_quiet(self):
        cmd_line = ['-q']
        self.config.parseOptions(cmd_line)
        self.assertEqual(log.LEVEL, log.Levels.WARNING)

    def test_verbose_contradictory(self):
        cmd_line = ['-q', '-v']
        self.config.parseOptions(cmd_line)
        self.assertEqual(log.LEVEL, log.DEFAULT_LEVEL)

class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        config = Options()
        config.parseOptions(['-r', '-b', '--remote', 'dummy'])
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
