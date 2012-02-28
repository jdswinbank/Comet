# VOEvent messages.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

from .xml import xml_document

ElementTree.register_namespace("voe", "http://www.ivoa.net/xml/VOEvent/v2.0")

def broker_test_message(ivo):
    """
    Test message which is regularly broadcast to all subscribers.
    """
    root_element = ElementTree.Element("{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent",
        attrib={
            "ivorn": ivo + "#TestEvent-%s" % datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "role": "test",
            "version": "2.0",
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
        }
    )
    who = ElementTree.SubElement(root_element, "Who")
    author_ivorn = ElementTree.SubElement(who, "AuthorIVORN")
    author_ivorn.text = ivo
    date = ElementTree.SubElement(who, "Date")
    date.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    return xml_document(root_element)
