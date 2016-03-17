# Comet VOEvent Broker.
# IP whitelisting factory.

from ipaddress import ip_address
from twisted.protocols.policies import WrappingFactory
import comet.log as log

__all__ = ["WhitelistingFactory"]

class WhitelistingFactory(WrappingFactory):
    def __init__(self, wrappedFactory, whitelist, connection_type="connection"):
        self.whitelist = whitelist
        self.connection_type = connection_type
        WrappingFactory.__init__(self, wrappedFactory)

    def buildProtocol(self, addr):
        remote_ip = ip_address(addr.host)
        if any(remote_ip in network for network in self.whitelist):
            return WrappingFactory.buildProtocol(self, addr)
        else:
            log.info("Attempted %s from non-whitelisted %s" % (self.connection_type, str(addr)))
            return None
