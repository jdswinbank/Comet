# Comet VOEvent Broker.
# Check for previously seen events.

from twisted.internet.threads import deferToThread
from zope.interface import implementer

from comet.icomet import IValidator
import comet.log as log

__all__ = ["CheckPreviouslySeen"]

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
            log.warn("Event DB lookup failed!")
            log.warn(failure.getTraceback())
            return failure

        return deferToThread(
            self.event_db.check_event,
            event,
        ).addCallbacks(check_validity, db_failure)
