# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import os
import anydbm
import datetime
from contextlib import closing
from threading import Lock

class IVORN_DB(object):
    # Using one big lock for all the databases is a little clunky.
    def __init__(self, root):
        self.root = root
        self.lock = Lock()

    def check_ivorn(self, ivorn):
        db_path, key = ivorn.split('//')[1].split('#')
        db_path = db_path.replace(os.path.sep, "_")
        try:
            self.lock.acquire()
            db = anydbm.open(os.path.join(self.root, db_path), 'c')
            if db.has_key(key):
                return False # Should not forward
            else:
                db[key] = str(datetime.datetime.utcnow())
                return True # Ok to forward
        finally:
            self.lock.release()
