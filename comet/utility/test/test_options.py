# Comet VOEvent Broker.
# Tests for standard options.

from argparse import ArgumentTypeError
from contextlib import redirect_stderr
from os import devnull

from twisted.trial import unittest

import comet.log as log
from comet.utility import valid_ivoid, valid_xpath, BaseOptions

class valid_TestCaseBase(object):
    def test_valid(self):
        self.assertEqual(self.validator(self.valid_expression),
                         self.valid_expression)

    def test_invalid(self):
        self.assertRaises(ArgumentTypeError, self.validator,
                          self.invalid_expression)


class valid_xpathTestCase(valid_TestCaseBase, unittest.TestCase):
    def setUp(self):
        self.validator = valid_xpath
        self.valid_expression = "/*[local-name()=\"VOEvent\" and @role=\"test\"]"
        self.invalid_expression = "\/\/\/\/\/"


class valid_ivoroidTestCase(valid_TestCaseBase, unittest.TestCase):
    def setUp(self):
        self.validator = valid_ivoid
        self.valid_expression = "ivo://comet/test"
        self.invalid_expression = "invalid"


class BaseOptionsTestCase(unittest.TestCase):
    ARGNAME, ARGVALUE = "test-argument", "test-value"
    PROGNAME="BaseOptionsTestCase-ProgName"

    def setUp(self):
        class TrivialOptions(BaseOptions):
            """Demonstrate core features of option parsing.
            """
            PROG=self.PROGNAME
            def _configureParser(self):
                self.parser.add_argument(f"--{BaseOptionsTestCase.ARGNAME}")
                self.has_been_checked = False

            def _checkOptions(self):
                # Demonstrates that _checkOptions has been invoked by the
                # superclass.
                self.has_been_checked = True

        self.trivial = TrivialOptions()

    def test_good_parse(self):
        self.assertFalse(self.trivial.has_been_checked)
        self.trivial.parseOptions([f"--{self.ARGNAME}", self.ARGVALUE])
        self.assertIn(self.ARGNAME.replace("-", "_"), self.trivial)
        self.assertEqual(self.trivial[self.ARGNAME.replace("-", "_")],
                         self.ARGVALUE)
        self.assertTrue(self.trivial.has_been_checked)

    def test_bad_parse(self):
        # Redirect stderr to avoid spewing unhelpful errors to the console
        # during testing.
        with redirect_stderr(open(devnull, 'w')):
            self.assertRaises(SystemExit,
                              self.trivial.parseOptions,
                              [f"--bad-arg", self.ARGVALUE])

    def test_missing_option(self):
        with self.assertRaises(KeyError):
            self.trivial['no-such-option']

    def test_prog(self):
        # TrivialOptions sets its progname.
        self.assertEqual(self.trivial.parser.prog, self.PROGNAME)

        # But a parser which doesn't is equally valid.
        class NoProgOptions(BaseOptions):
            pass
        self.assertNotEqual(NoProgOptions(), self.PROGNAME)

    def test_verbose(self):
        # By default, verbosity is not set.
        self.trivial.parseOptions([])
        self.assertEqual(self.trivial['verbose'], None)
        self.assertEqual(log.LEVEL, log.Levels.WARNING)

        # But it can be set once...
        self.trivial.parseOptions(["--verbose"])
        self.assertEqual(self.trivial['verbose'], 1)
        self.assertEqual(log.LEVEL, log.Levels.INFO)

        # ...or more.
        self.trivial.parseOptions(["--verbose", "-v"])
        self.assertEqual(self.trivial['verbose'], 2)
        self.assertEqual(log.LEVEL, log.Levels.DEBUG)
