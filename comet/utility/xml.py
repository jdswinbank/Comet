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

    @property
    def valid_signature(self):
        return False

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
