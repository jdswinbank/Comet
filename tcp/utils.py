# VOEvent transport protocol utility functions.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
from cStringIO import StringIO

# XML handling with lxml
import lxml.etree as ElementTree


def serialize_element_to_xml(et_element):
    """
    Serialise an ElementTree element to an XML string.

    Note that we prepend an XML declaration, which means we need
    ElementTree.write() rather than simply calling tostring() on the element.
    """
    s = StringIO()
    ElementTree.ElementTree(et_element).write(s, encoding="UTF-8", xml_declaration=True)
    return s.getvalue()
