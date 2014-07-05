# Comet VOEvent Broker.
# Event database.
# John Swinbank, <swinbank@transientskp.org>.

import os
import anydbm
import time
from hashlib import sha1
from threading import Lock
from collections import defaultdict

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList

from ..utility import log

class Event_DB(object):
    def __init__(self, root):
        self.root = root
        self.databases = defaultdict(Lock)

    @staticmethod
    def _get_event_details(event):
        db_path = event.attrib['ivorn'].split('//')[1].split('#')[0].replace(os.path.sep, "_")
        key = sha1(event.text).hexdigest()
        return db_path, key

    def check_event(self, event):
        """
        Returns True if event is unseen (and hence good to forward), False
        otherwise.
        """
        db_path, key = self._get_event_details(event)
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
        Remove entries with age at least expiry_time seconds from the database.
        """
        def expire_db(db_path, lock):
            remove = []
            lock.acquire()
            db = anydbm.open(os.path.join(self.root, db_path), 'c')
            # The database returned by anydbm is guaranteed to have a .keys()
            # method, but not necessarily .(iter)items().
            for key in db.keys():
                value = db[key]
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
                if int(time.time() - db_time) >= expiry_time:
                    # Rounding to nearest int avoids an issue when we call
                    # call prune(0) *immediately* after an insertion and might
                    # get hit by floating point weirdness.
                    remove.append(key)
            log.msg("Expiring %d events from %s" % (len(remove), db_path))
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
