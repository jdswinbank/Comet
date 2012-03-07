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
    ERROR = 300

# Levels.INFO is the default level.
try:
    LEVEL
except NameError:
    LEVEL = Levels.INFO

# The basic logging function.
def log(level, message):
    """
    Write a message to the Twisted log with an appropriate prefix, assuming it
    meets our verbosity criteria.
    """
    if level >= LEVEL:
        if level >= Levels.ERROR:
            twisted_log.err("[ERROR] %s" % (message,))
        elif level >= Levels.INFO:
            twisted_log.msg(" [INFO] %s" % (message,))
        else:
            twisted_log.msg("[DEBUG] %s" % (message,))

# Shortcuts to enable easy logging at the given level.
def error(message):
    log(Levels.ERROR, message)
# Alias for twisted.python.log compatibility
err = error

def info(message):
    log(Levels.INFO, message)
# Alias for twisted.python.log compatibility
msg = info

def debug(message):
    log(Levels.DEBUG, message)
