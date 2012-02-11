# Comet VOEvent Broker.
# Event validators.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from twisted.python import log
from twisted.internet.threads import deferToThread
import lxml.etree as etree

class SchemaValidator(object):
    """
    This takes an ElementTree element, converts it to a string, then reads
    that into lxml for validation. That... can't be optimal.
    """
    def __init__(self, schema):
        self.schema = etree.XMLSchema(etree.parse(schema))

    def __call__(self, protocol, event):
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

def CheckPreviouslySeen(object):
    def __init__(self, ivorn_db):
        self.ivorn_db = ivorn_db

    def __call__(self, protocol, event):
        def check_validity(is_valid):
            if is_valid:
                log.msg("Event not previously seen")
                return True
            else:
                log.msg("Event HAS been previously seen")
                raise Exception("Previously seen event")

        def db_failure(failure):
            log.err("IVORN DB lookup failed!")
            return failure

        return deferToThread(
            self.ivorn_db.check_ivorn,
            event.attrib['ivorn']
        ).addCallbacks(check_validity, db_failure)
