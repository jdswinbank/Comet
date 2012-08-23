from twisted.trial import unittest
from zope.interface import implementer

from ...icomet import IAuthenticatable
from ..auth import CheckSignatureMixin
from ..auth import check_auth

class DummyClass(CheckSignatureMixin):
    def __init__(self, must_auth, authenticated):
        self.must_auth = must_auth
        self.authenticated = authenticated

    @check_auth
    def test_function(self):
        return True

@implementer(IAuthenticatable)
class AuthenticatableDummyClass(DummyClass):
    pass

class CheckSignatureTestCase(unittest.TestCase):
    def setUp(self):
        self.dummy = DummyClass(True, False)

    def test_authenticate(self):
        self.assertFalse(self.dummy.authenticated)
        self.dummy.authenticate(None)
        self.assertTrue(self.dummy.authenticated)

class CheckAuthTestCase(unittest.TestCase):
    def test_bad_interface(self):
        dummy = DummyClass(False, False)
        self.assertEqual(dummy.test_function(), None)
        dummy = DummyClass(False, True)
        self.assertEqual(dummy.test_function(), None)
        dummy = DummyClass(True, True)
        self.assertEqual(dummy.test_function(), None)

    def test_no_auth_required(self):
        dummy = AuthenticatableDummyClass(False, False)
        self.assertEqual(dummy.test_function(), True)
        dummy = AuthenticatableDummyClass(False, True)
        self.assertEqual(dummy.test_function(), True)

    def test_auth_valid(self):
        dummy = AuthenticatableDummyClass(True, True)
        self.assertEqual(dummy.test_function(), True)

    def test_auth_invalid(self):
        dummy = AuthenticatableDummyClass(True, False)
        self.assertEqual(dummy.test_function(), None)
