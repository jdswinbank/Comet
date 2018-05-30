# Comet VOEvent Broker.
# Event database.

import os
try:
    import anydbm
except ImportError:
    import dbm as anydbm
import time
from hashlib import sha1
from threading import Lock
from collections import defaultdict
from contextlib import closing

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList

import comet.log as log
from comet.utility.voevent import parse_ivoid

__all__ = ["Event_DB"]

class Event_DB(object):
    def __init__(self, root):
        self.root = self._ensure_dir(root)
        self.databases = defaultdict(Lock)

    @staticmethod
    def _get_event_details(event):
        auth, rsrc, local = parse_ivoid(event.element.attrib['ivorn'])
        db_path = os.path.join(auth, rsrc).replace(os.path.sep, "_")
        key = sha1(event.raw_bytes).hexdigest()
        return db_path, key

    @staticmethod
    def _ensure_dir(path):
        """
        Check that ``path`` exists, is a directory, and has appropriate
        permissions for use as an event database.
        """
        # This check can't be bulletproof: there's nothing we can do to
        # prevent directories being removed or permissions being changed after
        # we've started. The aim here is to fail fast on startup for the sake
        # of user convenience, rather than to take robust security precautions.
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise RuntimeError("Event database is not a directory.")
        elif not os.access(path, os.R_OK | os.W_OK | os.X_OK):
            raise RuntimeError("Insufficient permissions to manipulate event database.")
        return path

    def check_event(self, event):
        """
        Returns True if event is unseen (and hence good to forward), False
        otherwise.
        """
        try:
            db_path, key = self._get_event_details(event)
        except Exception as e:
            log.warn("Unparseable IVOID; failing eventdb lookup");
        else:
            with self.databases[db_path]: # Acquire lock
                with closing(anydbm.open(os.path.join(self.root, db_path), 'c')) as db:
                    if not key in db:
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
                    if int(time.time() - float(db[key])) >= expiry_time:
                        # Rounding to nearest int avoids an issue when we call
                        # call prune(0) *immediately* after an insertion and might
                        # get hit by floating point weirdness.
                        remove.append(key)
                log.info("Expiring %d events from %s" % (len(remove), db_path))
                for key in remove: del db[key]
                db.close()

        return DeferredList(
            [
                deferToThread(expire_db, db_path, lock)
                for db_path, lock in self.databases.items()
            ]
        )
