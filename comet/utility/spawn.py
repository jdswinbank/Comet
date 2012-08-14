# Comet VOEvent Broker.
# Event handler to send an event to an external tool.
# John Swinbank, <swinbank@transientskp.org>, 2012.

import os

from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.protocol import ProcessProtocol

from zope.interface import implementer
from ..icomet import IHandler

from ..log import log

class SpawnCommandProtocol(ProcessProtocol):
    def __init__(self, deferred, text):
        self.deferred = deferred
        self.text = text

    def connectionMade(self):
        self.transport.write(self.text)
        self.transport.closeStdin()

    def processEnded(self, reason):
        if reason.value.exitCode:
            self.deferred.errback(
                Exception(
                    "Process returned non-zero (%d)" % (reason.value.exitCode,)
                )
            )
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
        log.msg("Running external command: %s" % (self.cmd,))
        reactor.spawnProcess(
            SpawnCommandProtocol(d, event.text),
            self.cmd,
            args=self.args,
            env=os.environ
        )
        return d
