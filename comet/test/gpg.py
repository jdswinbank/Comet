import os
import shutil
import tempfile
try:
    import gpgme
    import gpgme.editutil
    SKIP_GPG_TESTS = None
except ImportError, e:
    SKIP_GPG_TESTS = "PyGPGME not available (%s)" % (str(e))

from twisted.trial import unittest
from comet.utility.xml import xml_document
from comet.test.support import DUMMY_VOEVENT

class GPGTestSupport(unittest.TestCase):
    """
    7C4CA1BD is an ideal GPG key:

        - It has ID ivo://comet.broker/test
        - The secret key is available

    If trusted, it can always make good signatures.
    """
    skip = SKIP_GPG_TESTS
    PASSPHRASE = "comet"
    KEY_ID = "7C4CA1BD"

    def setUp(self):
        self._gpghome = tempfile.mkdtemp(prefix="tmp.gpghome")
        os.environ["GNUPGHOME"] = self._gpghome
        ctx = gpgme.Context()
        with open(os.path.join(os.path.dirname(__file__), "comet.secret.asc"), 'r') as k_fp:
            ctx.import_(k_fp)
        with open(os.path.join(os.path.dirname(__file__), "comet.public.asc"), 'r') as k_fp:
            ctx.import_(k_fp)

    def tearDown(self):
        del os.environ["GNUPGHOME"]
        shutil.rmtree(self._gpghome, ignore_errors=True)

    def _sign_untrusted(self, doc):
        doc.sign(self.PASSPHRASE, self.KEY_ID)
        return doc

    def _sign_trusted(self, doc):
        ctx = gpgme.Context()
        gpgme.editutil.edit_trust(ctx, ctx.get_key(self.KEY_ID, True), gpgme.VALIDITY_ULTIMATE)
        return self._sign_untrusted(doc)

class GPGTestSupportPublicOnlyKey(GPGTestSupport):
    """
    00D9DDEE does not have a secret key available: it cannot be used for
    signing events.
    """
    KEY_ID = "00D9DDEE"

class GPGTestSupportIndirectKey(GPGTestSupport):
    """
    E0EEF740 does not have a user name corresponding to the broker test IVORN.
    It can therefore only be used for signing when countersigned by 7C4CA1BD.
    """
    KEY_ID = "E0EEF740"

    def _sign_indirect_key(self):
        """
        Signs our key, E0EEF740, with 7C4CA1BD, and marks 7C4CA1BD as trusted.
        """
        ctx = gpgme.Context()
        ctx.passphrase_cb = lambda uid_hint, passphrase_info, pre_was_bad, fd: os.write(fd, "%s\n" % self.PASSPHRASE)
        signing_key = ctx.get_key("7C4CA1BD", True)
        gpgme.editutil.edit_trust(ctx, signing_key, gpgme.VALIDITY_ULTIMATE)
        ctx.signers = [signing_key]
        key = ctx.get_key(self.KEY_ID)
        gpgme.editutil.edit_sign(ctx, key, check=0)

class GPGTestSupportNonExtantKey(GPGTestSupport):
    """
    NONEXTANT is not a real key. It can never be used.
    """
    KEY_ID = "NONEXTANT"
