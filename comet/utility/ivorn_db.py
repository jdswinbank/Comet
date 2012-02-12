# Comet VOEvent Broker.
# IVORN database.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

import os
import anydbm
import datetime
from threading import Lock
from collections import defaultdict

from twisted.python import log
from twisted.internet.threads import deferToThread

from zope.interface import implements
from ..icomet import IValidator

class IVORN_DB(object):
    def __init__(self, root):
        self.root = root
        self.locks = defaultdict(Lock)

    def check_ivorn(self, ivorn):
        db_path, key = ivorn.split('//')[1].split('#')
        db_path = db_path.replace(os.path.sep, "_")
        try:
            self.locks[db_path].acquire()
            db = anydbm.open(os.path.join(self.root, db_path), 'c')
            if db.has_key(key):
                return False # Should not forward
            else:
                db[key] = str(datetime.datetime.utcnow())
                return True # Ok to forward
        finally:
            self.locks[db_path].release()

class CheckPreviouslySeen(object):
    implements(IValidator)
    def __init__(self, ivorn_db):
        self.ivorn_db = ivorn_db

    def __call__(self, event):
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
