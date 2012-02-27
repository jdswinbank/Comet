import lxml.etree as ElementTree

class xml_document(object):
    __slots__ = ["element", "text"]

    def __init__(self, document):
        if isinstance(document, ElementTree._Element):
            self.element = document
            self.text =  ElementTree.tostring(
                self.element,
                xml_declaration=True,
                encoding="UTF-8",
                pretty_print=True
            )
        else:
            self.text = document
            self.element = ElementTree.fromstring(self.text)

    @property
    def valid_signature(self):
        return False

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
