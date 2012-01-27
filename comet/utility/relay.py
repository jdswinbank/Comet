# VOEvent Broker.
# John Swinbank, <swinbank@transientskp.org>, 2012.

import os.path
import comet
from twisted.python import log
from twisted.internet.threads import deferToThread
from ..tcp.protocol import VOEventSubscriberFactory
from ..tcp.protocol import VOEventReceiverFactory
import lxml.etree as etree

def publish_event(protocol, event):
    """
    Forward an event to all subscribers, unless we've seen the IVORN
    previously.
    """
    log.msg("Rebroadcasting event to subscribers")
    for publisher in protocol.factory.publisher_factory.publishers:
        publisher.send_element(event)

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
            event
        ).addCallbacks(check_validity, schema_failure)

def previously_seen(protocol, event):
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
        protocol.factory.ivorn_db.check_ivorn,
        event.attrib['ivorn']
    ).addCallbacks(check_validity, db_failure)

class RelayingVOEventReceiverFactory(VOEventReceiverFactory):
    def __init__(self, local_ivo, publisher_factory, ivorn_db):
        VOEventReceiverFactory.__init__(self, local_ivo, [
                previously_seen,
                SchemaValidator(
                    os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")
                )
            ],
            [publish_event]
        )
        self.publisher_factory = publisher_factory
        self.ivorn_db = ivorn_db

class RelayingVOEventSubscriberFactory(VOEventSubscriberFactory):
    def __init__(self, local_ivo, publisher_factory, ivorn_db):
        VOEventSubscriberFactory.__init__(self, local_ivo, [previously_seen], [publish_event])
        self.publisher_factory = publisher_factory
        self.ivorn_db = ivorn_db
