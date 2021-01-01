# Comet VOEvent Broker.
# VOEvent transport protocol messages.

# Python standard library
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

from comet.utility import xml_document

__all__ = ["TransportMessage"]

ElementTree.register_namespace(
    "trn", "http://www.telescope-networks.org/xml/Transport/v1.1"
)


class TransportMessage(xml_document):

    # NB: ordering within packet must be per schema --
    # Origin, Response, Timestamp, Meta.

    @property
    def origin(self):
        return self.element.find("Origin").text

    @staticmethod
    def _root_element():
        return ElementTree.Element(
            "{http://www.telescope-networks.org/xml/Transport/v1.1}Transport",
            attrib={
                "version": "1.0",
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://telescope-networks.org/schema/Transport/v1.1 http://www.telescope-networks.org/schema/Transport-v1.1.xsd",
            },
        )

    @classmethod
    def _origin_response_element(cls, local_ivo, remote_ivo):
        root_element = cls._root_element()
        origin = ElementTree.SubElement(root_element, "Origin")
        origin.text = remote_ivo
        if local_ivo:
            response = ElementTree.SubElement(root_element, "Response")
            response.text = local_ivo
        timestamp = ElementTree.SubElement(root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return root_element

    @classmethod
    def iamalive(cls, local_ivo):
        root_element = cls._root_element()
        root_element.set("role", "iamalive")
        origin = ElementTree.SubElement(root_element, "Origin")
        origin.text = local_ivo
        timestamp = ElementTree.SubElement(root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(root_element)

    @classmethod
    def iamaliveresponse(cls, local_ivo, remote_ivo):
        root_element = cls._origin_response_element(local_ivo, remote_ivo)
        root_element.set("role", "iamalive")
        return cls(root_element)

    @classmethod
    def ack(cls, local_ivo, remote_ivo):
        root_element = cls._origin_response_element(local_ivo, remote_ivo)
        root_element.set("role", "ack")
        return cls(root_element)

    @classmethod
    def nak(cls, local_ivo, remote_ivo, result=None):
        root_element = cls._origin_response_element(local_ivo, remote_ivo)
        root_element.set("role", "nak")
        if result:
            meta = ElementTree.SubElement(root_element, "Meta")
            result_element = ElementTree.SubElement(meta, "Result")
            result_element.text = result
        return cls(root_element)

    @classmethod
    def authenticate(cls, local_ivo):
        root_element = cls._root_element()
        root_element.set("role", "authenticate")
        origin = ElementTree.SubElement(root_element, "Origin")
        origin.text = local_ivo
        timestamp = ElementTree.SubElement(root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(root_element)

    @classmethod
    def authenticateresponse(cls, local_ivo, remote_ivo, filters):
        root_element = cls._origin_response_element(local_ivo, remote_ivo)
        root_element.set("role", "authenticate")
        meta = ElementTree.SubElement(root_element, "Meta")
        for my_filter in filters:
            ElementTree.SubElement(
                meta, "Param", attrib={"name": "xpath-filter", "value": my_filter}
            )
        return cls(root_element)
