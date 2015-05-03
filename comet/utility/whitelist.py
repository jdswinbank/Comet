# Comet VOEvent Broker.
# IP whitelisting factory.
# John Swinbank, <swinbank@transientskp.org>.

from ipaddress import ip_address

from twisted.protocols.policies import WrappingFactory

from ..utility import log

class WhitelistingFactory(WrappingFactory):
    def __init__(self, wrappedFactory, whitelist):
        self.whitelist = whitelist
        WrappingFactory.__init__(self, wrappedFactory)

    def buildProtocol(self, addr):
        remote_ip = ip_address(addr.host)
        if any(remote_ip in network for network in self.whitelist):
            return WrappingFactory.buildProtocol(self, addr)
        else:
            log.msg("Attempted submission from non-whitelisted %s" % str(addr))
            return None
