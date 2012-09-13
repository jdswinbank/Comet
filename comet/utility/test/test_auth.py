from twisted.trial import unittest
from zope.interface import implementer

from ...icomet import IAuthenticatable
from ...utility import log
from ...test.support import DUMMY_VOEVENT
from ...test.gpg import GPGTestSupport
from ...test.gpg import GPGTestSupportPublicOnlyKey

from ..auth import check_for_bad_key
from ..auth import CheckSignatureMixin
from ..auth import check_auth
from ..auth import check_sig
from ..xml import xml_document

class DummyTransport(object):
    def getPeer(self):
        return "(Dummy Peer)"

    def loseConnection(self):
        pass

class DummyClass(CheckSignatureMixin):
    def __init__(self, must_auth, authenticated):
        self.must_auth = must_auth
        self.authenticated = authenticated
        self.transport = DummyTransport()

    @check_auth
    def test_function(self):
        return True

@implementer(IAuthenticatable)
class AuthenticatableDummyClass(DummyClass):
    pass

class CheckSignatureTestCase(GPGTestSupport):
    def setUp(self):
        GPGTestSupport.setUp(self)
        self.authenticator = DummyClass(True, False)

    def test_authenticate(self):
        self.assertFalse(self.authenticator.authenticated)
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_trusted(doc)
        d = self.authenticator.authenticate(doc)
        d.addCallback(lambda x: self.assertTrue(self.authenticator.authenticated))
        return d

class check_sigTestCase(GPGTestSupport):
    def test_bad_sig(self):
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_untrusted(doc)
        d = check_sig(doc)
        d.addCallback(lambda x: self.assertFalse(x))
        return d

    def test_good_sig(self):
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_trusted(doc)
        d = check_sig(doc)
        d.addCallback(lambda x: self.assertTrue(x))
        return d

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

class GoodKeyTestCase(GPGTestSupport):
    def test_key(self):
        self.assertFalse(check_for_bad_key(self.ctx.get_key(self.KEY_ID)))

class RevokedKeyTestCase(GPGTestSupport):
    def test_key(self):
        self._revoke_key()
        self.assertTrue(check_for_bad_key(self.ctx.get_key(self.KEY_ID)))
