# VOEvent transport protocol messages.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

from ..utility.xml import xml_document

ElementTree.register_namespace("trn", "http://www.telescope-networks.org/xml/Transport/v1.1")

# NB: ordering within packet must be per schema --
# Origin, Response, Timestamp, Meta.

def transport_message():
    return xml_document(
        ElementTree.Element("{http://www.telescope-networks.org/xml/Transport/v1.1}Transport",
            attrib={
                "version": "1.0",
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://telescope-networks.org/schema/Transport/v1.1 http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
            }
        )
    )

def origin_response_message(local_ivo, remote_ivo):
    root_element = transport_message().element
    origin = ElementTree.SubElement(root_element, "Origin")
    origin.text = remote_ivo
    response = ElementTree.SubElement(root_element, "Response")
    response.text = local_ivo
    timestamp = ElementTree.SubElement(root_element, "TimeStamp")
    timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return xml_document(root_element)

def iamalive(local_ivo):
    root_element = transport_message().element
    root_element.set("role", "iamalive")
    origin = ElementTree.SubElement(root_element, "Origin")
    origin.text = local_ivo
    timestamp = ElementTree.SubElement(root_element, "TimeStamp")
    timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return xml_document(root_element)

def iamaliveresponse(local_ivo, remote_ivo):
    root_element = origin_response_message(local_ivo, remote_ivo).element
    root_element.set("role", "iamalive")
    return xml_document(root_element)

def ack(local_ivo, remote_ivo):
    root_element = origin_response_message(local_ivo, remote_ivo).element
    root_element.set("role", "ack")
    return xml_document(root_element)

def nak(local_ivo, remote_ivo, result=None):
    root_element = origin_response_message(local_ivo, remote_ivo).element
    root_element.set("role", "nak")
    if result:
        meta = ElementTree.SubElement(root_element, "Meta")
        result_element = ElementTree.SubElement(meta, "Result")
        result_element.text = result
    return xml_document(root_element)

def authenticate(local_ivo):
    root_element = transport_message().element
    root_element.set("role", "authenticate")
    origin = ElementTree.SubElement(root_element, "Origin")
    origin.text = local_ivo
    timestamp = ElementTree.SubElement(root_element, "TimeStamp")
    timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return xml_document(root_element)

def authenticateresponse(local_ivo, remote_ivo, filters):
    root_element = origin_response_message(local_ivo, remote_ivo).element
    root_element.set("role", "authenticate")
    meta = ElementTree.SubElement(root_element, "Meta")
    for my_filter in filters:
        xslt = ElementTree.SubElement(meta, "filter", attrib={"type": "xpath"})
        xslt.text = my_filter
    return xml_document(root_element)
