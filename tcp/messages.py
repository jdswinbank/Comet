# VOEvent transport protocol messages.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
from datetime import datetime

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

from .utils import serialize_element_to_xml

# For neatness only; requires Python 2.7
#ElementTree.register_namespace("trn", "http://www.telescope-networks.org/xml/Transport/v1.1")

# NB: ordering must be per schema --
# Origin, Response, Timestamp, Meta.

class TransportMessage(object):
    """
    Base class for Transport protocol messages.

    Provides a Transport packet with a timestamp.
    """
    def __init__(self):
        self.root_element = ElementTree.Element("{http://www.telescope-networks.org/xml/Transport/v1.1}Transport",
            attrib={
                "version": "1.0",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://telescope-networks.org/schema/Transport/v1.1 http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
            }
        )

    def to_string(self):
        """
        Serialise the message to an XML string.
        """
        return serialize_element_to_xml(self.root_element)

class OriginResponseMessage(TransportMessage):
    """
    Specialist Transport packet which includes Origin and Response elements.
    """
    def __init__(self, local_ivo, remote_ivo):
        super(OriginResponseMessage, self).__init__()
        origin = ElementTree.SubElement(self.root_element, "Origin")
        origin.text = remote_ivo
        response = ElementTree.SubElement(self.root_element, "Response")
        response.text = local_ivo
        timestamp = ElementTree.SubElement(self.root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

class IAmAlive(TransportMessage):
    """
    Specialist Transport packet with an "iamalive" role and an Origin element.
    """
    def __init__(self, local_ivo):
        super(IAmAlive, self).__init__()
        self.root_element.set("role", "iamalive")
        origin = ElementTree.SubElement(self.root_element, "Origin")
        origin.text = local_ivo
        timestamp = ElementTree.SubElement(self.root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

class IAmAliveResponse(OriginResponseMessage):
    """
    Specialist Transport packet with an "iamalive" role and Origin and
    Response elements.
    """
    def __init__(self, local_ivo, remote_ivo):
        super(IAmAliveResponse, self).__init__(local_ivo, remote_ivo)
        self.root_element.set("role", "iamalive")

class Ack(OriginResponseMessage):
    """
    Specialist Transport packet with an "ack" role.
    """
    def __init__(self, local_ivo, remote_ivo):
        super(Ack, self).__init__(local_ivo, remote_ivo)
        self.root_element.set("role", "ack")

class Nak(OriginResponseMessage):
    """
    Specialist Transport packet with an "nak" role.
    """
    def __init__(self, local_ivo, remote_ivo):
        super(Nak, self).__init__(local_ivo, remote_ivo)
        self.root_element.set("role", "nak")
