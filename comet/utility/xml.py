import os
import re
import io
import sys
import lxml.etree as ElementTree
from functools import wraps
from ..utility import log
from ..utility.exceptions import CometGPGSigFailedException
try:
    import gpgme
except ImportError, e:
    log.debug("GPG not available (%s)" % (str(e),))

def require(modulename):
    """
    Refuse to execute a function if the named module isn't available.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not modulename in sys.modules:
                raise NotImplementedError("%s not available." % (modulename,))
            else:
                return f(*args, **kwargs)
        return wrapper
    return decorator

def dash_escape(text):
    """
    Replace all instances of '^' in text with '\^', then all instances of '-'
    with '^'.
    """
    return text.replace("^", "\^").replace("-", "^")

def dash_unescape(text):
    """
    Replace all instances of '^' *not* prefixed with '\' by '-', then replace
    all instances of '\^' by '^'.
    """
    # Keep repeating until all overlapping patterns have been replaced.
    count = True
    while count:
        text, count = re.subn(r"(^|[^\\])\^", r"\1-", text)
    return text.replace("\^", "^")

def check_for_bad_key(key):
    if key.expired:
        return "Expired"
    elif key.disabled:
        return "Disabled"
    elif key.invalid:
        return "Invalid"
    elif key.revoked:
        return "Revoked"
    elif not key.can_sign:
        return "Not capable of signing"
    else:
        return False

class xml_document(object):
    __slots__ = ["_element", "_text"]

    def __init__(self, document):
        if isinstance(document, ElementTree._Element):
            self.element = document
        else:
            self.text = document

    def get_text(self):
        return self._text
    def set_text(self, value):
        self._text = value
        self._element = ElementTree.fromstring(self._text)
    text = property(get_text, set_text)

    def get_element(self):
        return self._element
    def set_element(self, value):
        self._element = value
        self._text =  ElementTree.tostring(
            self._element,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True
        )
    element = property(get_element, set_element)

    @require("gpgme")
    def sign(self, passphrase, key_id):
        # We never want to fall back to a GPG agent; the user must provide
        # their passphrase directly..
        os.unsetenv("GPG_AGENT_INFO")
        passphrase_cb = lambda uid_hint, passphrase_info, pre_was_bad, fd: os.write(fd, "%s\n" % passphrase)

        input_stream = io.BytesIO(self.signable_text)
        output_stream = io.BytesIO()

        ctx = gpgme.Context()
        ctx.armor = True
        ctx.passphrase_cb = passphrase_cb
        try:
            ctx.signers = [ctx.get_key(key_id, False)]
        except gpgme.GpgmeError:
            raise CometGPGSigFailedException("Cannot load key %s" % (key_id,))

        bad_key = check_for_bad_key(ctx.signers[0])
        if bad_key:
            raise CometGPGSigFailedException("Key %s is unusable: %s" % (key_id, bad_key))

        try:
            signature = ctx.sign(input_stream, output_stream, gpgme.SIG_MODE_DETACH)
        except gpgme.GpgmeError, e:
            raise CometGPGSigFailedException("gpgme failed: %s" % (str(e),))

        sig_text = dash_escape(output_stream.getvalue())
        if not sig_text:
            raise CometGPGSigFailedException("Signature text is empty")
        self.text = "%s<!--\n%s\n-->" % (self.text, sig_text)

    @require("gpgme")
    def valid_signature(self, required_identity=None):
        plaintext = io.BytesIO(self.signable_text)
        signature = io.BytesIO(self.signature)
        ctx = gpgme.Context()
        ctx.keylist_mode = gpgme.KEYLIST_MODE_SIGS
        good_sig = False
        try:
            sigs = ctx.verify(signature, plaintext, None)
            for sig in sigs:
                log.debug("Checking sig... %s" % (str(sig)))
                if sig.status:
                    # Status is only set if the signature had an error;
                    # We skip to the next signature
                    continue
                base_uid = ctx.get_key(sig.fpr).uids[0]
                for sig in base_uid.signatures:
                    uid = ctx.get_key(sig.keyid).uids[0]
                    if uid.validity in (gpgme.VALIDITY_FULL, gpgme.VALIDITY_ULTIMATE):
                        if not required_identity or uid.name == required_identity:
                            good_sig = True
                            break
        except gpgme.GpgmeError:
            pass
        except Exception, e:
            log.msg(e)
        finally:
            return good_sig

    @property
    def signable_text(self):
        # We sign:
        #  - The XML declaration with no trailing newline;
        #  - The root element with no trailing newline.
        # Any comments outside the root element are not signed; comments
        # within are signed.
        e_match = re.search(r"(<\?xml.*?>).*(<(\S*):(VOEvent|Transport).*>.*</(\3):(\4)>)",
            self.text, re.DOTALL | re.IGNORECASE | re.MULTILINE
        )
        if e_match:
            return e_match.groups()[0] + e_match.groups()[1]
        else:
            return None

    @property
    def signature(self):
        sig_match = re.search(
            r"(\^{5}BEGIN PGP SIGNATURE\^{5}.*\^{5}END PGP SIGNATURE\^{5})",
            self.text, re.DOTALL | re.MULTILINE
        )
        if sig_match:
            return dash_unescape(sig_match.groups()[0])
        else:
            return None

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
