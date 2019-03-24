# Comet VOEvent Broker.
# XML document parsing.

import lxml.etree as ElementTree

__all__ = ["ParseError", "xml_document"]

# Used to infer incoming message type
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')
TRANSPORT_ROLES = ('iamalive', 'ack', 'nak', 'authenticate')

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

    @property
    def role(self):
        return self.element.get('role')

    def __init__(self, document):
        if isinstance(document, ElementTree._Element):
            self.element = document
        else:
            self.raw_bytes = document

    def get_raw_bytes(self):
        return self._raw_bytes
    def set_raw_bytes(self, value):
        if not isinstance(value, bytes):
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

    @staticmethod
    def infer_type(raw_bytes):
        """Given a payload, attempt to infer its message type.
        """
        # The double-parse is unfortunate.
        xmldoc = xml_document(raw_bytes)
        if xmldoc.role in VOEVENT_ROLES:
            from comet.utility.voevent import VOEventMessage
            return VOEventMessage(raw_bytes)
        elif xmldoc.role in TRANSPORT_ROLES:
            from comet.protocol import TransportMessage
            return TransportMessage(raw_bytes)
        else:
            raise ParseError(f"Unknown role: {xmldoc.role}")

    @staticmethod
    def from_stream(stream):
        """Give an IO stream, return an appropriate xml_document subclass.
        """
        return xml_document.infer_type(stream.read())
