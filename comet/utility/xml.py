import os
import re
import io
import lxml.etree as ElementTree

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

    def sign(self, passphrase, key_id=None):
        import gpgme
        passphrase_cb = lambda uid_hint, passphrase_info, pre_was_bad, fd: os.write(fd, "%s\n" % passphrase)

        input_stream = io.BytesIO(self.voevent_element_text)
        output_stream = io.BytesIO()

        ctx = gpgme.Context()
        ctx.armor = True
        ctx.passphrase_cb = passphrase_cb
        if key_id:
            ctx.signers = [ctx.get_key(key_id)]

        signature = ctx.sign(input_stream, output_stream, gpgme.SIG_MODE_DETACH)

        sig_text = output_stream.getvalue().replace(
            "-----BEGIN PGP SIGNATURE-----",
            "=====BEGIN PGP SIGNATURE====="
        ).replace(
            "-----END PGP SIGNATURE-----",
            "=====END PGP SIGNATURE====="
        )
        self.text = "%s<!--\n%s\n-->" % (self.voevent_element_text, sig_text)

    def valid_signature(self):
        import gpgme
        plaintext = io.BytesIO(self.voevent_element_text)
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
    def voevent_element_text(self):
        voe_match = re.search(r"(<(\S*)VOEvent.*>.*</(\2)VOEvent>)",
            self.text, re.DOTALL | re.IGNORECASE | re.MULTILINE
        )
        if voe_match:
            return voe_match.groups()[0]
        else:
            return None

    @property
    def signature(self):
        sig_match = re.search(
            r"(=====BEGIN PGP SIGNATURE=====.*=====END PGP SIGNATURE=====)",
            self.text, re.DOTALL | re.MULTILINE
        )
        if sig_match:
            return sig_match.groups()[0].replace(
                "=====BEGIN PGP SIGNATURE=====",
                "-----BEGIN PGP SIGNATURE-----"
            ).replace(
                "=====END PGP SIGNATURE=====",
                "-----END PGP SIGNATURE-----"
            )
        else:
            return None

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
