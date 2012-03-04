# Comet VOEvent Broker.
# IP whitelisting factory.
# John Swinbank, <swinbank@transientskp.org>, 2012.

from ipaddr import IPAddress

from twisted.python import log
from twisted.internet.protocol import ServerFactory

class WhitelistingFactory(ServerFactory):
    def __init__(self, whitelist):
        self.whitelist = whitelist

    def buildProtocol(self, addr):
        remote_ip = IPAddress(addr.host)
        if any(remote_ip in network for network in self.whitelist):
            return ServerFactory.buildProtocol(self, addr)
        else:
            log.msg("Attempted submission from non-whitelisted %s" % str(addr))
            return None
