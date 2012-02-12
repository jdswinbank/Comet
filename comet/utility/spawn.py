# Comet VOEvent Broker.
# Event handler to send an event to an external tool.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from subprocess import Popen, PIPE, CalledProcessError

from twisted.python import log
from twisted.internet.threads import deferToThread

from zope.interface import implements
from ..icomet import IHandler

class SpawnCommand(object):
    """
    Send a VOEvent to standard input of an external command.
    """
    implements(IHandler)
    name = "spawn-command"

    def __init__(self, cmd):
        self.cmd = cmd

    def __call__(self, event):
        def run_cmd(cmd, text):
            log.msg("Running external command: %s" % (self.cmd,))
            process = Popen([self.cmd], stdin=PIPE)
            process.communicate(text)
            process.wait()
            if process.returncode:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            else:
                return process.returncode
        return deferToThread(run_cmd, self.cmd, event.original)
