import os

from twisted.trial import unittest

import comet
from ...icomet import IValidator
from ..signature import CheckSignature

class ValidEvent(object):
    def valid_signature(self):
        return True

class InvalidEvent(object):
    def valid_signature(self):
        return False

class CheckSignatureTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = CheckSignature()

    def test_valid(self):
        self.assertTrue(self.validator(ValidEvent()))

    def test_invalid(self):
        self.assertTrue(self.validator(InvalidEvent()))

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.validator))
