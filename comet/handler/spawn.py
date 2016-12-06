# Comet VOEvent Broker.
# Event handler to spawn an external command & supply a VOEvent on stdin.

import os

from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.protocol import ProcessProtocol

from zope.interface import implementer
from comet.icomet import IHandler
import comet.log as log

__all__ = ["SpawnCommand"]

class SpawnCommandProtocol(ProcessProtocol):
    # Assume that all external processes write a UTF-8 bytestream to STDOUT.
    # This is obviously a questionable assumption, but it's not clear what a
    # better alternative would be (probably trying to auto-detect, but that's
    # error prone).
    STDOUT_ENCODING = "UTF-8"

    def __init__(self, deferred, raw_bytes):
        self.deferred = deferred
        self.raw_bytes = raw_bytes

    def connectionMade(self):
        # Note that we're squiring whatever encoding raw_bytes happens to be
        # in at the process.
        self.transport.write(self.raw_bytes)
        self.transport.closeStdin()

    def outReceived(self, data):
        log.debug("External process said: %s" %
                  (data.decode(self.STDOUT_ENCODING),))

    def errReceived(self, data):
        self.outReceived(data)

    def processEnded(self, reason):
        if reason.value.exitCode:
            self.deferred.errback(reason)
        else: self.deferred.callback(True)

@implementer(IHandler)
class SpawnCommand(object):
    """
    Send a VOEvent to standard input of an external command.
    """
    name = "spawn-command"

    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.args = [cmd]
        self.args.extend(args)

    def __call__(self, event):
        d = defer.Deferred()
        log.info("Running external command: %s" % (self.cmd,))
        reactor.spawnProcess(
            SpawnCommandProtocol(d, event.raw_bytes),
            self.cmd,
            args=self.args,
            env=os.environ
        )
        def log_reason(reason):
            """
            Catch a Failure returned from an unsuccessful process execution
            and log the return value, then re-raise the error.
            """
            if not os.access(self.cmd, os.X_OK):
                msg = "%s is not an executable" % (self.cmd,)
            else:
                msg = "%s returned non-zero (%d)" % (self.cmd,
                                                     reason.value.exitCode)
            log.warn(msg)
            return reason
        d.addErrback(log_reason)
        return d
