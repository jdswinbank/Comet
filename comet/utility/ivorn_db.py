# Comet VOEvent Broker.
# IVORN database.
# John Swinbank, <swinbank@transientskp.org>, 2012.

import os
import anydbm
import time
from threading import Lock
from collections import defaultdict

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList

from zope.interface import implements
from ..icomet import IValidator

from ..log import log

class IVORN_DB(object):
    def __init__(self, root):
        self.root = root
        self.databases = defaultdict(Lock)

    def check_ivorn(self, ivorn):
        """
        Returns True if ivorn is unseen (and hence good to forward), False
        otherwise.
        """
        db_path, key = ivorn.split('//')[1].split('#')
        db_path = db_path.replace(os.path.sep, "_")
        try:
            self.databases[db_path].acquire()
            db = anydbm.open(os.path.join(self.root, db_path), 'c')
            try:
                if db.has_key(key):
                    return False # Should not forward
                else:
                    db[key] = str(time.time())
                    return True # Ok to forward
            finally:
                db.close()
        finally:
            self.databases[db_path].release()

    def prune(self, expiry_time):
        """
        Remove entries older than expiry_time seconds from the database.
        """
        def expire_db(db_path, lock):
            remove = []
            lock.acquire()
            db = anydbm.open(os.path.join(self.root, db_path), 'c')
            for key, value in db.iteritems():
                try:
                    # New style databases store seconds since the epoch
                    db_time = float(value)
                except ValueError:
                    # Old style databases store %Y-%m-%d %H:%M:%S.ssss
                    # Parse that...
                    integral_part, fractional_part = value.split('.')
                    db_time = time.mktime(
                        time.strptime(integral_part, "%Y-%m-%d %H:%M:%S")
                    ) + float('0.' + fractional_part)
                    # ...and update db to new format.
                    db[key] = str(db_time)
                if time.time() - db_time > expiry_time:
                    remove.append(key)
            log.msg("Expiring %d IVORNs from %s" % (len(remove), db_path))
            for key in remove: del db[key]
            db.close()
            lock.release()

        return DeferredList(
            [
                deferToThread(expire_db, db_path, lock)
                for db_path, lock in self.databases.iteritems()
            ],
            consumeErrors=True
        )


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
                raise Exception("Previously seen by this broker")

        def db_failure(failure):
            log.err("IVORN DB lookup failed!")
            return failure

        return deferToThread(
            self.ivorn_db.check_ivorn,
            event.attrib['ivorn']
        ).addCallbacks(check_validity, db_failure)
