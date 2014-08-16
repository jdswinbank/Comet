# Comet VOEvent Broker.
# Event database.
# John Swinbank, <swinbank@transientskp.org>.

import os
import anydbm
import time
from hashlib import sha1
from threading import Lock
from collections import defaultdict
from contextlib import closing

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList

from comet.utility import log
from comet.utility.voevent import parse_ivorn

class Event_DB(object):
    def __init__(self, root):
        self.root = root
        self.databases = defaultdict(Lock)

    @staticmethod
    def _get_event_details(event):
        auth, rsrc, local = parse_ivorn(event.attrib['ivorn'])
        db_path = os.path.join(auth, rsrc).replace(os.path.sep, "_")
        key = sha1(event.text).hexdigest()
        return db_path, key

    def check_event(self, event):
        """
        Returns True if event is unseen (and hence good to forward), False
        otherwise.
        """
        try:
            db_path, key = self._get_event_details(event)
        except:
            log.warn("Unparseable IVORN; failing eventdb lookup");
        else:
            with self.databases[db_path]: # Acquire lock
                with closing(anydbm.open(os.path.join(self.root, db_path), 'c')) as db:
                    if not db.has_key(key):
                        db[key] = str(time.time())
                        return True
        return False

    def prune(self, expiry_time):
        """
        Remove entries with age at least expiry_time seconds from the database.
        """
        def expire_db(db_path, lock):
            remove = []
            with lock:
                db = anydbm.open(os.path.join(self.root, db_path), 'c')
                # The database returned by anydbm is guaranteed to have a
                # .keys() method, but not necessarily .(iter)items().
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

        return DeferredList(
            [
                deferToThread(expire_db, db_path, lock)
                for db_path, lock in self.databases.iteritems()
            ]
        )
