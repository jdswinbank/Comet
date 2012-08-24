import os
import shutil
import tempfile
import gpgme
import gpgme.editutil

from twisted.trial import unittest
from comet.utility.xml import xml_document
from comet.test.support import DUMMY_VOEVENT

class GPGTestSupport(unittest.TestCase):
    PASSPHRASE = "comet"
    KEY_ID = "71837D03"

    def setUp(self):
        self._gpghome = tempfile.mkdtemp(prefix="tmp.gpghome")
        os.environ["GNUPGHOME"] = self._gpghome
        ctx = gpgme.Context()
        with open(os.path.join(os.path.dirname(__file__), "comet.secret.asc"), 'r') as k_fp:
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
