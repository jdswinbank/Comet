# Comet VOEvent Broker.
# Check for previously seen events.
# John Swinbank, <swinbank@transientskp.org>.

from twisted.internet.threads import deferToThread
from zope.interface import implementer

from ..icomet import IValidator
from ..utility import log
from ..utility.event_db import Event_DB

@implementer(IValidator)
class CheckPreviouslySeen(object):
    def __init__(self, event_db):
        self.event_db = event_db

    def __call__(self, event):
        def check_validity(is_valid):
            if is_valid:
                log.debug("Event not previously seen")
                return True
            else:
                log.debug("Event HAS been previously seen")
                raise Exception("Previously seen by this broker")

        def db_failure(failure):
            log.warning("Event DB lookup failed!")
            log.err(failure)
            return failure

        return deferToThread(
            self.event_db.check_event,
            event,
        ).addCallbacks(check_validity, db_failure)
