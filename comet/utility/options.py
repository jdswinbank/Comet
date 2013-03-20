import sys
from twisted.python import usage

class BaseOptions(usage.Options):
    def postOptions(self):
        if 'passphrase-file' in self and self['passphrase-file']:
            try:
                with open(self['passphrase-file'], 'r') as f:
                    self['passphrase'] = f.read()
            except IOError:
                print("Couldn't read passphrase from %s; exiting." % self['passphrase-file'])
                sys.exit(1)
        else:
            self['passphrase'] = None
