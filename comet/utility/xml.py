import lxml.etree as ElementTree

class xml_document(object):
    __slots__ = ["element", "original"]

    def __init__(self, original):
        self.original = original
        self.element = ElementTree.fromstring(original)

    @property
    def valid_signature(self):
        return True

    def __getattr__(self, name):
        try:
            return getattr(self.element, name)
        except AttributeError:
            raise AttributeError, name
