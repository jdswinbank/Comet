from twisted.trial import unittest

from ..auth import check_auth

class DummyClass(object):
    def __init__(self, must_auth, authenticated):
        self.must_auth = must_auth
        self.authenticated = authenticated

    @check_auth
    def test_function(self):
        return True

class CheckAuthTestCase(unittest.TestCase):
    def test_no_auth_required(self):
        dummy = DummyClass(False, False)
        self.assertEqual(dummy.test_function(), True)
        dummy = DummyClass(False, True)
        self.assertEqual(dummy.test_function(), True)

    def test_auth_valid(self):
        dummy = DummyClass(True, True)
        self.assertEqual(dummy.test_function(), True)

    def test_auth_invalid(self):
        dummy = DummyClass(True, False)
        self.assertNotEqual(dummy.test_function(), True)
