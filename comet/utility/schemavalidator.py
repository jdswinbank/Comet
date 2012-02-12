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
        def check_validity(is_valid):
            if is_valid:
                log.msg("Schema validation passed")
                return True
            else:
                log.msg("Schema validation failed")
                raise Exception("Schema validation failed")

        def schema_failure(failure):
            log.err("Schema validator failed!")
            return failure

        return deferToThread(
            self.schema.validate,
            event.element
        ).addCallbacks(check_validity, schema_failure)
