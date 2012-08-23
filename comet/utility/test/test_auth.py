import shutil
import gpgme
import os
import tempfile

from twisted.trial import unittest
from zope.interface import implementer

from ...log import log
from ...icomet import IAuthenticatable
from ..auth import CheckSignatureMixin
from ..auth import check_auth
from ..xml import xml_document
from ...test.support import DUMMY_VOEVENT

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
    PASSPHRASE = "comet"
    KEY_ID = "71837D03"

    def setUp(self):
        self._gpghome = tempfile.mkdtemp(prefix="tmp.gpghome")
        os.environ["GNUPGHOME"] = self._gpghome
        ctx = gpgme.Context()
        with open(os.path.join(os.path.dirname(__file__), "comet.secret.asc"), 'r') as k_fp:
            ctx.import_(k_fp)
        gpgme.editutil.edit_trust(ctx, ctx.get_key(self.KEY_ID, True), gpgme.VALIDITY_ULTIMATE)
        self.authenticator = DummyClass(True, False)

    def tearDown(self):
        del os.environ["GNUPGHOME"]
        shutil.rmtree(self._gpghome, ignore_errors=True)

    def test_authenticate(self):
        self.assertFalse(self.authenticator.authenticated)
        doc = xml_document(DUMMY_VOEVENT)
        doc.sign(self.PASSPHRASE, self.KEY_ID)
        log.msg(doc.text)
        d = self.authenticator.authenticate(doc)
        d.addCallback(lambda x: self.assertTrue(self.authenticator.authenticated))
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
