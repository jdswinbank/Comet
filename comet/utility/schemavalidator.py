# Comet VOEvent Broker.
# Schema validator.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from twisted.python import log
from twisted.internet.threads import deferToThread
import lxml.etree as etree

from zope.interface import implements
from ..icomet import IValidator

class SchemaValidator(object):
    """
    This takes an ElementTree element, converts it to a string, then reads
    that into lxml for validation. That... can't be optimal.
    """
    implements(IValidator)

    def __init__(self, schema):
        self.schema = etree.XMLSchema(etree.parse(schema))

    def __call__(self, event):
        return deferToThread(self.schema.assertValid, event.element)

