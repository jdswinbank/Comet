# Comet VOEvent Broker.
# XML document parsing.

from comet import BINARY_TYPE
import lxml.etree as ElementTree

__all__ = ["ParseError", "xml_document"]

class ParseError(Exception):
    pass

class xml_document(object):
    """
    The combination of of an ElementTree element and its serialization.

    We want to preserve the raw bytes received (ie, not some reformatted
    version thereof) in case some future version needs them for e.g. checking
    a cryptographic signature. Note this is _raw bytes_, not some decoded
    unicode string. The raw bytes will (generally) include the XML encoding
    declaration, but if it is not available we will rely on lxml to take its
    best guess.
    """
    __slots__ = ["_element", "_raw_bytes"]

    def __init__(self, document):
        if isinstance(document, ElementTree._Element):
            self.element = document
        else:
            self.raw_bytes = document

    def get_raw_bytes(self):
        return self._raw_bytes
    def set_raw_bytes(self, value):
        if not isinstance(value, BINARY_TYPE):
            raise ParseError("Raw bytes required.")
        self._raw_bytes = value

        # We'll disable entity expansion in the parser to avoid any risk of
        # resource exhaustion. If we receive any, we raise (and hence reject
        # the event). Better safe than sorry.
        parser = ElementTree.XMLParser(resolve_entities=False)
        try:
            element = ElementTree.fromstring(self._raw_bytes, parser=parser)
        except ElementTree.ParseError as e:
            raise ParseError(str(e))
        if list(element.iter(ElementTree.Entity)):
            raise ParseError("Entity expansion not supported")
        else:
            self._element = element
    raw_bytes = property(get_raw_bytes, set_raw_bytes)

    def get_element(self):
        return self._element
    def set_element(self, value):
        self._element = value
        self._raw_bytes = ElementTree.tostring(
            self._element,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True
        )
    element = property(get_element, set_element)

    @property
    def valid_signature(self):
        return False

    @property
    def encoding(self):
        # Return the encoding that lxml detected for the raw_bytes we're
        # carrying. Note we need to construct an ElementTree and use that;
        # can't read from the element directly.
        return ElementTree.ElementTree(self._element).docinfo.encoding
