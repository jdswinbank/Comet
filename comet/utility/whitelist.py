# Comet VOEvent Broker.
# IP whitelisting factory.

from ipaddress import ip_address
from twisted.protocols.policies import WrappingFactory
import comet.log as log

__all__ = ["WhitelistingFactory"]


class WhitelistingFactory(WrappingFactory):
    """Wrap a factory so that it only accepts connections from given addresses.

    Notes
    -----
    Only addresses with a hostname (IPv4, IPv6, SSL, etc) can be wrapped.
    Others (e.g. Unix domain sockets) bypass the whitelist and are always
    accepted.
    """

    def __init__(self, wrappedFactory, whitelist, connection_type="connection"):
        self.whitelist = whitelist
        self.connection_type = connection_type
        WrappingFactory.__init__(self, wrappedFactory)

    def buildProtocol(self, addr):
        try:
            remote_ip = ip_address(addr.host)
            if not any(remote_ip in network for network in self.whitelist):
                log.info(
                    f"Attempted {self.connection_type} from " f"non-whitelisted {addr}"
                )
                return None
        except AttributeError:
            log.warn(f"Bypassing whitelist for {self.connection_type} " f"from {addr}")
        return WrappingFactory.buildProtocol(self, addr)

    def __getattr__(self, name):
        """Delegate attribute access to the wrapped factory."""
        if hasattr(self.wrappedFactory, name):
            return getattr(self.wrappedFactory, name)
        else:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
            )
