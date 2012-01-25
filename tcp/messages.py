# VOEvent transport protocol messages.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

ElementTree.register_namespace("trn", "http://www.telescope-networks.org/xml/Transport/v1.1")

# NB: ordering within packet must be per schema --
# Origin, Response, Timestamp, Meta.

def transport_message():
    return ElementTree.Element("{http://www.telescope-networks.org/xml/Transport/v1.1}Transport",
        attrib={
            "version": "1.0",
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://telescope-networks.org/schema/Transport/v1.1 http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        }
    )

def origin_response_message(local_ivo, remote_ivo):
    root_element = transport_message()
    origin = ElementTree.SubElement(root_element, "Origin")
    origin.text = remote_ivo
    response = ElementTree.SubElement(root_element, "Response")
    response.text = local_ivo
    timestamp = ElementTree.SubElement(root_element, "TimeStamp")
    timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return root_element

def iamalive(local_ivo):
    root_element = transport_message()
    root_element.set("role", "iamalive")
    origin = ElementTree.SubElement(root_element, "Origin")
    origin.text = local_ivo
    timestamp = ElementTree.SubElement(root_element, "TimeStamp")
    timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return root_element

def iamaliveresponse(local_ivo, remote_ivo):
    root_element = origin_response_message(local_ivo, remote_ivo)
    root_element.set("role", "iamalive")
    return root_element

def ack(local_ivo, remote_ivo):
    root_element = origin_response_message(local_ivo, remote_ivo)
    root_element.set("role", "ack")
    return root_element

def nak(local_ivo, remote_ivo):
    root_element = origin_response_message(local_ivo, remote_ivo)
    root_element.set("role", "nak")
    return root_element
