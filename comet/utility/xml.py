import os
import re
import io
import sys
import lxml.etree as ElementTree
from functools import wraps
from ..utility import log
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
    def sign(self, passphrase, key_id=None):
        passphrase_cb = lambda uid_hint, passphrase_info, pre_was_bad, fd: os.write(fd, "%s\n" % passphrase)

        input_stream = io.BytesIO(self.element_text)
        output_stream = io.BytesIO()

        ctx = gpgme.Context()
        ctx.armor = True
        ctx.passphrase_cb = passphrase_cb
        if key_id:
            ctx.signers = [ctx.get_key(key_id)]

        signature = ctx.sign(input_stream, output_stream, gpgme.SIG_MODE_DETACH)

        sig_text = dash_escape(output_stream.getvalue())
        self.text = "%s<!--\n%s\n-->" % (self.element_text, sig_text)

    @require("gpgme")
    def valid_signature(self):
        plaintext = io.BytesIO(self.element_text)
        signature = io.BytesIO(self.signature)
        ctx = gpgme.Context()
        good_sig = False
        try:
            [sig] = ctx.verify(signature, plaintext, None)
            if sig.validity in (gpgme.VALIDITY_FULL, gpgme.VALIDITY_ULTIMATE):
                good_sig = True
        except gpgme.GpgmeError:
            pass
        finally:
            return good_sig

    @property
    def element_text(self):
        # We sign everything from the start of the XML declaration to the end
        # of the element.
        e_match = re.search(r"(<\?xml.*</\S*(VOEvent|Transport)>)",
            self.text, re.DOTALL | re.IGNORECASE | re.MULTILINE
        )
        if e_match:
            return e_match.groups()[0]
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
