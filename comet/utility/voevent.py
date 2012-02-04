# VOEvent messages.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# Python standard library
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

ElementTree.register_namespace("voe", "http://www.ivoa.net/xml/VOEvent/v2.0")

def dummy_voevent_message(ivo):
    """
    Dummy VOEvent message for test purposes only.
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
    return root_element
