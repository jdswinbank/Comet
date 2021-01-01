# Comet VOEvent Broker.
# Tests for standard options.

import os
from argparse import ArgumentTypeError
from tempfile import TemporaryDirectory
from textwrap import dedent

from twisted.plugin import getPlugins
from twisted.trial import unittest

import comet.plugins
import comet.log as log
from comet.icomet import IHandler
from comet.utility import valid_ivoid, valid_xpath, BaseOptions
from comet.testutils import OptionTestUtils


class valid_TestCaseBase(object):
    def test_valid(self):
        self.assertEqual(self.validator(self.valid_expression), self.valid_expression)

    def test_invalid(self):
        self.assertRaises(ArgumentTypeError, self.validator, self.invalid_expression)


class valid_xpathTestCase(valid_TestCaseBase, unittest.TestCase):
    def setUp(self):
        self.validator = valid_xpath
        self.valid_expression = '/*[local-name()="VOEvent" and @role="test"]'
        self.invalid_expression = r"/////"


class valid_ivoroidTestCase(valid_TestCaseBase, unittest.TestCase):
    def setUp(self):
        self.validator = valid_ivoid
        self.valid_expression = "ivo://comet/test"
        self.invalid_expression = "invalid"


class BaseOptionsTestCase(unittest.TestCase, OptionTestUtils):
    ARGNAME, ARGVALUE = "test-argument", "test-value"
    PROGNAME = "BaseOptionsTestCase-ProgName"

    def setUp(self):
        class TrivialOptions(BaseOptions):
            """Demonstrate core features of option parsing."""

            PROG = self.PROGNAME

            def _configureParser(self):
                self.parser.add_argument(f"--{BaseOptionsTestCase.ARGNAME}")
                self.has_been_checked = False

            def _checkOptions(self):
                # Demonstrates that _checkOptions has been invoked by the
                # superclass.
                self.has_been_checked = True

        self.config = TrivialOptions()

    def test_good_parse(self):
        self.assertFalse(self.config.has_been_checked)
        self.config.parseOptions([f"--{self.ARGNAME}", self.ARGVALUE])
        self.assertIn(self.ARGNAME.replace("-", "_"), self.config)
        self.assertEqual(self.config[self.ARGNAME.replace("-", "_")], self.ARGVALUE)
        self.assertTrue(self.config.has_been_checked)

    def test_bad_parse(self):
        # Redirect stderr to avoid spewing unhelpful errors to the console
        # during testing.
        self._check_bad_parse(["--bad-arg", self.ARGVALUE])

    def test_missing_option(self):
        self.assertFalse("no-such-option" in self.config)
        with self.assertRaises(KeyError):
            self.config["no-such-option"]

    def test_prog(self):
        # TrivialOptions sets its progname.
        self.assertEqual(self.config.parser.prog, self.PROGNAME)

        # But a parser which doesn't is equally valid.
        class NoProgOptions(BaseOptions):
            pass

        self.assertNotEqual(NoProgOptions(), self.PROGNAME)

    def test_verbose(self):
        # By default, verbosity is not set.
        self.config.parseOptions([])
        self.assertEqual(self.config["verbose"], None)
        self.assertEqual(log.LEVEL, log.Levels.WARNING)

        # But it can be set once...
        self.config.parseOptions(["--verbose"])
        self.assertEqual(self.config["verbose"], 1)
        self.assertEqual(log.LEVEL, log.Levels.INFO)

        # ...or more.
        self.config.parseOptions(["--verbose", "-v"])
        self.assertEqual(self.config["verbose"], 2)
        self.assertEqual(log.LEVEL, log.Levels.DEBUG)

    def test_pluginpath(self):
        # The COMET_PLUGINPATH environment variable should set the locations
        # set for plugins.
        dummy_plugin = dedent(
            f"""
        # Comet VOEvent Broker.
        # This is a no-op plugin, used to demonstrate plugin registration.

        from zope.interface import implementer
        from twisted.plugin import IPlugin
        from comet.icomet import IHandler

        # Event handlers must implement IPlugin and IHandler.
        @implementer(IPlugin, IHandler)
        class TestPlugin(object):
            name = "test-plugin-{os.getpid()}"

            # When the handler is called, it is passed an instance of
            # comet.utility.xml.xml_document.
            def __call__(self, event):
                pass

        # This instance of the handler is what actually constitutes our plugin.
        test_plugin = TestPlugin()"""
        )

        # We'll restore the initial environment at the end of the test case.
        init_environ = os.environ.copy()
        init_pluginpath = comet.plugins.__path__.copy()

        initial_plugin_count = len(list(getPlugins(IHandler, comet.plugins)))

        try:
            with TemporaryDirectory() as tempdir:
                with open(os.path.join(tempdir, "plugin.py"), "w") as f:
                    f.write(dummy_plugin)

                os.environ["COMET_PLUGINPATH"] = tempdir

                # Trigger update of comet.plugins.__path__
                BaseOptions()

                # Should now be one more plugin available.
                self.assertEqual(
                    len(list(getPlugins(IHandler, comet.plugins))),
                    initial_plugin_count + 1,
                )

        finally:
            os.environ = init_environ
            comet.plugins.__path__ = init_pluginpath

        # Should be back to the original plugin count.
        self.assertEqual(
            len(list(getPlugins(IHandler, comet.plugins))), initial_plugin_count
        )
