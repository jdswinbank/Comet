# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import os
import anydbm
import datetime
from contextlib import closing

class IVORN_DB(object):
    def __init__(self, root):
        self.root = root

    def check_ivorn(self, ivorn):
        db_path, key = ivorn.split('//')[1].split('#')
        db_path = db_path.replace(os.path.sep, "_")
        with closing(anydbm.open(os.path.join(self.root, db_path), 'c')) as db:
            if db.has_key(key):
                return False # Should not forward
            else:
                db[key] = str(datetime.datetime.utcnow())
                return True # Ok to forward
