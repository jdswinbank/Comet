import lxml.etree as ElementTree

class xml_document(object):
    __slots__ = ["_element", "_text"]

    def __init__(self, document):
        if isinstance(document, ElementTree._Element):
            self._element = document
        else:
            self._text = document

    @property
    def valid_signature(self):
        return True

    @property
    def element(self):
        if not hasattr(self, "_element"):
            self._element = ElementTree.fromstring(self.text)
        return self._element

    @property
    def text(self):
        if not hasattr(self, "_text"):
            self._text =  ElementTree.tostring(
                self.element,
                xml_declaration=True,
                encoding="UTF-8",
                pretty_print=True
            )
        return self._text

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
