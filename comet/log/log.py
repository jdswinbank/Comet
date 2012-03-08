# Comet VOEvent Broker
# Logging system
# John Swinbank, <swinbank@transientskp.org>, 2012

# We define multiple log levels for use within Comet, and allow the user to
# adjust the verbosity with command line options. We then gate messages
# through to the Twisted logging system as appropriate.

from twisted.python import log as twisted_log

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
def log(level, message):
    """
    Write a message to the Twisted log with an appropriate prefix, assuming it
    meets our verbosity criteria.
    """
    if level >= LEVEL:
        if level >= Levels.WARNING:
            twisted_log.msg("[WARNING] %s" % (str(message),))
        elif level >= Levels.INFO:
            twisted_log.msg("[INFO] %s" % (str(message),))
        else:
            twisted_log.msg("[DEBUG] %s" % (str(message),))

# Shortcuts to enable easy logging at the given level.
def warning(message):
    log(Levels.WARNING, message)
warn = warning

def info(message):
    log(Levels.INFO, message)
# Alias for twisted.python.log compatibility
msg = info

def debug(message):
    log(Levels.DEBUG, message)

# Errors override our logging mechanism and get dumped straight into Twisted's
# log handlers, which can handle stack traces etc.
err = twisted_log.err
