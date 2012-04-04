# Comet VOEvent Broker
# Logging system
# John Swinbank, <swinbank@transientskp.org>, 2012

# We define multiple log levels for use within Comet, and allow the user to
# adjust the verbosity with command line options. We then gate messages
# through to the Twisted logging system as appropriate.

from twisted.python import log as twisted_log
from twisted.python import context
from twisted.internet import defer

class Levels(object):
    """
    Log levels available.
    """
    DEBUG = 100
    INFO  = 200
    WARNING = 300

# Levels.INFO is the default level.
DEFAULT_LEVEL = Levels.INFO
try:
    LEVEL
except NameError:
    LEVEL = DEFAULT_LEVEL

# The basic logging function.
def log(level, message, system=None):
    """
    Write a message to the Twisted log with an appropriate prefix, assuming it
    meets our verbosity criteria.
    """
    if not system:
        system = context.get(twisted_log.ILogContext)['system']
    if level >= LEVEL:
        if level >= Levels.WARNING:
            twisted_log.msg(message, system="WARNING %s" % (system,))
        elif level >= Levels.INFO:
            twisted_log.msg(message, system="INFO %s" % (system,))
        else:
            twisted_log.msg(message, system="DEBUG %s" % (system,))

class LogWithDeferred(object):
    """
    Forward a message to log(), above, and return a Deferred which we can
    chain off.
    """
    def __init__(self, level):
        self.level = level

    def __call__(self, message, system=None):
        log(self.level, message, system)
        return defer.succeed(None)

# Shortcuts to enable easy logging at the given level.
warning = LogWithDeferred(Levels.WARNING)
warn = warning

info = LogWithDeferred(Levels.INFO)
msg = info

debug = LogWithDeferred(Levels.DEBUG)

# Errors override our logging mechanism and get dumped straight into Twisted's
# log handlers, which can handle stack traces etc.
err = twisted_log.err
